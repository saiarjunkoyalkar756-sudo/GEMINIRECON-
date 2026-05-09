from agents.base_agent import BaseAgent
from tools.runner import ToolRunner
import asyncio

class ReconAgent(BaseAgent):
    def __init__(self, model_id=None):
        super().__init__(model_id=model_id, system_instruction="You are a Recon Agent. Execute tools and report real data.")
        
    async def chat_async(self, message):
        # The Orchestrator passes the "plan" as a message.
        # Here we extract the required tool and execute it.
        # This is a simplified integration.
        if "subfinder" in message.lower():
            target = message.split("-d")[-1].strip() if "-d" in message else "example.com"
            result = await ToolRunner.run("subfinder", target, args=f"-d {target}")
            return type('Response', (), {'text': result['file']})
        elif "nuclei" in message.lower():
            target = message.split("-target")[-1].strip() if "-target" in message else "example.com"
            result = await ToolRunner.run("nuclei", target, args=f"-target {target}")
            return type('Response', (), {'text': result['file']})
        
        # Fallback to LLM if no tool matched
        return await super().chat_async(message)
