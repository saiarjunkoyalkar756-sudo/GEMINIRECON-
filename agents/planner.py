from agents.base_agent import BaseAgent
from core.config import PROMPTS_DIR

class PlannerAgent(BaseAgent):
    def __init__(self, model_id=None):
        prompt_path = PROMPTS_DIR / "agents" / "planner.txt"
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
        super().__init__(model_id=model_id, system_instruction=system_instruction)
