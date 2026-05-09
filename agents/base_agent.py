import os
import asyncio
import time
import json
from google import genai
from google.genai import types
from google.api_core import exceptions
from openai import OpenAI
from core.config import GEMINI_API_KEY, GEMINI_MODEL, OPENROUTER_API_KEY, OPENROUTER_MODEL, LLM_PROVIDER
from core.utils.autotune import AutoTune
from core.utils.research.classify import Classifier

class BaseAgent:
    def __init__(self, model_id=None, system_instruction=None, tools=None):
        self.provider = LLM_PROVIDER
        self.system_instruction = system_instruction
        self.tools = tools or []
        self.history = []
        
        if self.provider == "gemini":
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model_id = model_id or GEMINI_MODEL
            self.chat = self.client.chats.create(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=self.tools
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
        if self.provider == "gemini":
            return await self._chat_gemini(message)
        else:
            return await self._chat_openrouter(message)

    async def _chat_gemini(self, message):
        max_retries = 3
        base_delay = 5
        
        # 1. Classify prompt for safety/context
        classification = Classifier.classify(message)
        
        # 2. History retrieval
        try:
            raw_history = self.chat.get_history()
            history = [{'role': p.role, 'content': p.parts[0].text} for p in raw_history if p.parts and p.parts[0].text]
        except Exception:
            history = []
            
        strategy = 'adaptive'
        if classification['domain'] in ['cyber', 'meta']:
            strategy = 'precise'
            
        tuned_params = AutoTune.get_params(message, history, strategy=strategy)
        
        # Note: google-genai SDK handles tool calls automatically if they are in the config
        # during a chat session.
        config_params = {
            'system_instruction': self.system_instruction,
            'tools': self.tools,
            'temperature': tuned_params.get('temperature'),
            'top_p': tuned_params.get('top_p'),
            'top_k': tuned_params.get('top_k'),
        }

        config = types.GenerateContentConfig(**config_params)

        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.chat.send_message(message, config=config)
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
        
        # Define tools for OpenAI format
        openai_tools = []
        for tool in self.tools:
            # We assume tools are passed as the actual function objects
            # and we need to provide their JSON schema.
            # For simplicity, we'll hardcode the schema for run_osint_tool
            if tool.__name__ == 'run_osint_tool':
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": "run_osint_tool",
                        "description": "Execute an OSINT tool command on the system.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The full command string to execute (e.g., 'subfinder -d example.com')"
                                }
                            },
                            "required": ["command"]
                        }
                    }
                })

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
                
                if not response_message.tool_calls:
                    # Final text response
                    class MockResponse:
                        def __init__(self, text):
                            self.text = text
                    return MockResponse(response_message.content)
                
                # Handle tool calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Find the tool in our self.tools
                    tool_func = None
                    for t in self.tools:
                        if t.__name__ == function_name:
                            tool_func = t
                            break
                    
                    if tool_func:
                        # Execute the tool
                        result = tool_func(**function_args)
                        self.history.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(result),
                        })
                    else:
                        self.history.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: Tool {function_name} not found",
                        })
            except Exception as e:
                print(f"OpenRouter Error: {e}")
                raise e
        
        raise Exception("Max tool execution turns exceeded for OpenRouter.")

    def get_history(self):
        if self.provider == "gemini":
            return self.chat.get_history()
        return self.history
