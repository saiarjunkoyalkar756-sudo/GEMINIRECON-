import asyncio
import json
from openai import AsyncOpenAI
from core.config import OPENROUTER_API_KEY, AI_MODEL
from core.storage.vector_store import VectorMemory

class CommanderAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        self.memory = VectorMemory()

    async def decide_next_step(self, target, history):
        """AI-driven decision making based on current knowledge graph."""
        state = self.memory.query(target)
        prompt = f"""
        Commander Agent: You are managing an offensive security scan on {target}.
        
        Recent Findings: {json.dumps(history)}
        Stored Knowledge: {json.dumps(state)}
        
        Decide the next best offensive action:
        1. Fuzzing (e.g., parameter injection)
        2. Recon (e.g., deeper crawling)
        3. Exploitation (e.g., XSS/SQLi injection)
        
        Return JSON plan with 'action', 'target_parameter', and 'reasoning'.
        """
        
        response = await self.client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": "You are a professional security commander."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
