from agents.base_agent import BaseAgent
from core.config import PROMPTS_DIR
from core.utils.tool_executor import run_osint_tool

class ReconAgent(BaseAgent):
    def __init__(self, model_id=None):
        prompt_path = PROMPTS_DIR / "agents" / "recon.txt"
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
        super().__init__(
            model_id=model_id, 
            system_instruction=system_instruction,
            tools=[run_osint_tool]
        )
