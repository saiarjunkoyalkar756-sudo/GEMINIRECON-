from agents.base_agent import BaseAgent
from skills.manager import skill_registry
from typing import Dict, Any, Optional
import json

class IntentAgent(BaseAgent):
    def __init__(self, model_id=None):
        skills_list = [f"- {s.name}: {s.objective}" for s in skill_registry.list_skills()]
        system_instruction = (
            "You are the Intent Classification Agent for GEMINIRECON. "
            "Your job is to analyze the user's request and determine the appropriate recon skill and target. "
            "Available Skills:\n" + "\n".join(skills_list) + "\n\n"
            "Return a JSON object with: 'skill', 'target', and 'reasoning'."
        )
        super().__init__(model_id=model_id, system_instruction=system_instruction)

    async def classify_intent(self, user_input: str) -> Dict[str, Any]:
        resp = await self.chat_async(f"Classify this request: {user_input}")
        text = resp.text
        # Basic JSON extraction
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(text[start:end])
        except:
            pass
        return {"skill": "default", "target": user_input, "reasoning": "Fallback to default"}
