import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Skill(BaseModel):
    name: str
    category: str
    objective: str
    methodology: List[str]
    prompt_template: str
    expected_outputs: List[str]
    tools_required: List[str] = []

class SkillRegistry:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self._load_skills()

    def _load_skills(self):
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            return

        for root, _, files in os.walk(self.skills_dir):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r") as f:
                            data = yaml.safe_load(f)
                            if data:
                                skill = Skill(**data)
                                self.skills[skill.name] = skill
                                logger.info(f"Loaded skill: {skill.name}")
                    except Exception as e:
                        logger.error(f"Error loading skill {path}: {e}")

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def list_skills(self) -> List[Skill]:
        return list(self.skills.values())

# Global registry
skill_registry = SkillRegistry()
