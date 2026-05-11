from agents.base_agent import BaseAgent
from skills.manager import skill_registry, Skill
from typing import Dict, Any, List
import json

class PlannerAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = (
            "You are the Recon Planner Agent. "
            "Based on a selected skill and target, create a detailed execution plan. "
            "The plan should be a list of tasks, where each task defines which tools to use and what to look for. "
            "Return a JSON object: {'tasks': [{'id': 1, 'description': '...', 'tool': '...', 'params': {...}}]}"
        )
        super().__init__(model_id=model_id, system_instruction=system_instruction)

    async def create_plan(self, skill_name: str, target: str) -> Dict[str, Any]:
        skill = skill_registry.get_skill(skill_name)
        context = f"Skill: {skill.name if skill else 'General Recon'}\nObjective: {skill.objective if skill else 'Gather info'}\nTarget: {target}"
        
        resp = await self.chat_async(f"Create an execution plan for:\n{context}")
        text = resp.text
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(text[start:end])
        except:
            pass
        return {"tasks": []}
