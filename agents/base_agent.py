import os
import asyncio
import time
import json
import logging
from google import genai
from google.genai import types
from google.api_core import exceptions
from openai import OpenAI
from core.config import GEMINI_API_KEY, GEMINI_MODEL, OPENROUTER_API_KEY, OPENROUTER_MODEL, LLM_PROVIDER
from tools.registry import registry
from execution.engine import execution_engine

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, model_id=None, system_instruction=None, tools=None):
        self.provider = LLM_PROVIDER
        self.system_instruction = system_instruction
        # tools can be a list of tool names or ToolDefinition objects
        self.tool_names = tools or [] 
        self.history = []
        
        # Resolve tool definitions from registry if names are provided
        self.resolved_tools = []
        for t in self.tool_names:
            if isinstance(t, str):
                tool_def = registry.get_tool(t)
                if tool_def:
                    self.resolved_tools.append(tool_def)
            else:
                self.resolved_tools.append(t)

        if self.provider == "gemini":
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model_id = model_id or GEMINI_MODEL
            
            # Gemini tool definitions
            gemini_tools = []
            if self.resolved_tools:
                # In the new SDK, we might need to convert our schema to what Gemini expects
                # or use function declarations.
                # For now, we'll use the OpenAI-style schemas which many providers understand
                # or adapt them as needed.
                gemini_tools = [types.Tool(function_declarations=[
                    types.FunctionDeclaration(
                        name=t.name,
                        description=t.description,
                        parameters=t.get_openai_schema()["function"]["parameters"]
                    ) for t in self.resolved_tools
                ])]

            self.chat = self.client.chats.create(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=gemini_tools
                )
            )
        else: # OpenRouter
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            self.model_id = model_id or OPENROUTER_MODEL
            if self.system_instruction:
                self.history.append({"role": "system", "content": self.system_instruction})

    async def chat_async(self, message):
        if self.provider == "openrouter":
            return await self._chat_openrouter(message)
        return await self._chat_gemini(message)

    async def _chat_gemini(self, message):
        max_retries = 3
        base_delay = 5
        
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                # Gemini SDK handles tool calling loops internally if configured, 
                # but we want more control or at least to see what's happening.
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.chat.send_message(message)
                )
                
                # Check for tool calls in response
                # Note: The SDK might handle execution if automatic tool calling is enabled.
                # If not, we handle it manually:
                while response.candidates[0].content.parts and any(p.function_call for p in response.candidates[0].content.parts):
                    tool_parts = [p.function_call for p in response.candidates[0].content.parts if p.function_call]
                    tool_responses = []
                    
                    for fc in tool_parts:
                        tool_name = fc.name
                        args = fc.args
                        logger.info(f"[Gemini] Tool Call: {tool_name} with args {args}")
                        
                        # Execute tool
                        result = await execution_engine.execute_tool(tool_name, args)
                        
                        tool_responses.append(types.Part(
                            function_response=types.FunctionResponse(
                                name=tool_name,
                                response={"result": str(result)}
                            )
                        ))
                    
                    # Send tool responses back to model
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.chat.send_message(tool_responses)
                    )
                
                return response
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "resource_exhausted" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                raise e
        raise Exception("Max retries exceeded for Gemini API call.")

    async def _chat_openrouter(self, message):
        self.history.append({"role": "user", "content": message})
        
        # Limit history to last 10 turns to save tokens
        if len(self.history) > 10:
            # Keep system instruction if it exists
            if self.history[0]["role"] == "system":
                self.history = [self.history[0]] + self.history[-9:]
            else:
                self.history = self.history[-10:]

        openai_tools = [t.get_openai_schema() for t in self.resolved_tools]

        max_turns = 10
        for _ in range(max_turns):
            loop = asyncio.get_event_loop()
            try:
                kwargs = {
                    "model": self.model_id,
                    "messages": self.history
                }
                if openai_tools:
                    kwargs["tools"] = openai_tools
                    kwargs["tool_choice"] = "auto"

                completion = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(**kwargs)
                )
                
                response_message = completion.choices[0].message
                self.history.append(response_message)
                
                if not hasattr(response_message, 'tool_calls') or not response_message.tool_calls:
                    # Final text response
                    class MockResponse:
                        def __init__(self, text):
                            self.text = text
                    return MockResponse(response_message.content)
                
                # Handle tool calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"[OpenRouter] Tool Call: {function_name} with args {function_args}")
                    
                    # Execute tool
                    result = await execution_engine.execute_tool(function_name, function_args)
                    
                    self.history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result),
                    })
            except Exception as e:
                logger.error(f"OpenRouter Error: {e}")
                raise e
        
        raise Exception("Max tool execution turns exceeded for OpenRouter.")

    def get_history(self):
        if self.provider == "gemini":
            return self.chat.get_history()
        return self.history
