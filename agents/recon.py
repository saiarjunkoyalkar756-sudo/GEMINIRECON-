from agents.base_agent import BaseAgent
from tools.registry import registry
import asyncio

class ReconAgent(BaseAgent):
    def __init__(self, model_id=None):
        # Pass all available recon tools to the BaseAgent
        recon_tools = [t.name for t in registry.list_tools() if t.category == "recon"]
        vuln_tools = [t.name for t in registry.list_tools() if t.category == "vuln"]
        
        super().__init__(
            model_id=model_id, 
            system_instruction=(
                "You are an expert Security Reconnaissance Agent. "
                "Your goal is to discover assets, open ports, and potential vulnerabilities on a given target. "
                "Use the provided tools to gather information. Always report real data found by the tools. "
                "Do not make assumptions or hallucinate findings."
            ),
            tools=recon_tools + vuln_tools
        )
