from agents.base_agent import BaseAgent
from tools.runner import ToolRunner
import asyncio

class ReconAgent(BaseAgent):
    def __init__(self, model_id=None):
        super().__init__(model_id=model_id, system_instruction="You are a Recon Agent. Execute tools and report real data.")
        
    async def chat_async(self, message):
        print(f"[DEBUG] ReconAgent received message: {message}")
        if "subfinder" in message.lower():
            # Extract domain more dynamically
            import re
            match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', message)
            target = match.group(1) if match else "example.com"
            result = await ToolRunner.run("subfinder", target, args=f"-d {target}")
            return type('Response', (), {'text': result['file']})
        elif "nuclei" in message.lower():
            # Extract domain
            import re
            match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', message)
            target = match.group(1) if match else "example.in"
            
            # Optimized Nuclei command to prevent hanging
            # Using -silent to reduce output, -no-interact to prevent hangs, and focused templates
            cmd = f"-l results/{target}/subdomains.txt -t cves/ -t exposures/ -t misconfigurations/ -silent -no-interact -o results/{target}/vulnerabilities.json"
            result = await ToolRunner.run("nuclei", target, args=cmd)
            return type('Response', (), {'text': result['file']})
        
        return await super().chat_async(message)
