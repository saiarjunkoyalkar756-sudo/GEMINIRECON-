import os
import asyncio
import time
from google import genai
from google.genai import types
from google.api_core import exceptions
from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.utils.autotune import AutoTune
from core.utils.research.classify import Classifier

class BaseAgent:
    def __init__(self, model_id=None, system_instruction=None, tools=None):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = model_id or GEMINI_MODEL
        self.system_instruction = system_instruction
        self.tools = tools or []
        
        self.chat = self.client.chats.create(
            model=self.model_id,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=self.tools
            )
        )

    async def chat_async(self, message):
        """
        Sends a message to Gemini and handles tool calls.
        Integrates AutoTune and Research Classifier.
        """
        max_retries = 3
        base_delay = 5
        
        # 1. Classify prompt for safety/context
        classification = Classifier.classify(message)
        
        # 2. AutoTune: Select optimal parameters
        try:
            raw_history = self.chat.get_history()
            history = [{'role': p.role, 'content': p.parts[0].text} for p in raw_history if p.parts and p.parts[0].text]
        except Exception:
            history = []
            
        # If classification flags cyber/intrusion, use 'precise' strategy for accuracy
        strategy = 'adaptive'
        if classification['domain'] in ['cyber', 'meta']:
            strategy = 'precise'
            
        tuned_params = AutoTune.get_params(message, history, strategy=strategy)
        # Build config dynamically to exclude unsupported parameters
        config_params = {
            'system_instruction': self.system_instruction,
            'tools': self.tools,
            'temperature': tuned_params.get('temperature'),
            'top_p': tuned_params.get('top_p'),
            'top_k': tuned_params.get('top_k'),
        }

        # Add penalties only if they are not the defaults that trigger errors
        if tuned_params.get('presence_penalty') is not None:
            config_params['presence_penalty'] = tuned_params.get('presence_penalty')
        if tuned_params.get('frequency_penalty') is not None:
            config_params['frequency_penalty'] = tuned_params.get('frequency_penalty')

        config = types.GenerateContentConfig(**config_params)

        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                # Use the new config for this specific call
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.chat.send_message(message, config=config)
                )
                return response
            except Exception as e:
                error_str = str(e).lower()
                # If invalid argument (penalty not supported), retry without penalties
                if "invalid_argument" in error_str or "penalty" in error_str:
                    config = types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        tools=self.tools,
                        temperature=tuned_params.get('temperature'),
                        top_p=tuned_params.get('top_p'),
                        top_k=tuned_params.get('top_k'),
                    )
                    continue
                if "429" in error_str or "resource_exhausted" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                raise e

        
        raise Exception("Max retries exceeded for Gemini API call.")

    def get_history(self):
        return self.chat.get_history()
