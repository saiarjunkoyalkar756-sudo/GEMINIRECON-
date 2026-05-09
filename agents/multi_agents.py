from agents.base_agent import BaseAgent
from core.config import PROMPTS_DIR, GEMINI_API_KEY
import os

class AnalysisAgent(BaseAgent):
    def __init__(self, model_id=None, use_ultraplinian=False):
        prompt_path = PROMPTS_DIR / "agents" / "analysis.txt"
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
        
        # Load Godmode if specifically requested or for high-stakes analysis
        self.use_ultraplinian = use_ultraplinian
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        super().__init__(model_id=model_id, system_instruction=system_instruction)

    async def analyze_with_race(self, recon_data: str):
        if not self.use_ultraplinian or not self.openrouter_key:
            return await self.chat_async(f"Analyze this recon data: {recon_data}")
            
        from core.utils.research.ultraplinian import Ultraplinian
        up = Ultraplinian()
        query = f"Provide a deep security analysis of this reconnaissance data. Extract all hidden assets, technology stacks, and potential attack vectors: {recon_data}"
        results = await up.race(query, self.openrouter_key)
        
        if results:
            winner = results[0]
            return type('Response', (), {'text': winner['content'], 'model': winner['model']})
        
        return await self.chat_async(query)

class RiskAgent(BaseAgent):
    def __init__(self, model_id=None):
        prompt_path = PROMPTS_DIR / "agents" / "risk.txt"
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class ReportAgent(BaseAgent):
    def __init__(self, model_id=None):
        prompt_path = PROMPTS_DIR / "agents" / "report.txt"
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class MemoryAgent(BaseAgent):
    def __init__(self, model_id=None):
        prompt_path = PROMPTS_DIR / "agents" / "memory.txt"
        with open(prompt_path, "r") as f:
            system_instruction = f.read()
        super().__init__(model_id=model_id, system_instruction=system_instruction)
