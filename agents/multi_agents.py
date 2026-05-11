from agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from core.utils.research.ultraplinian import Ultraplinian

class DecisionAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = (
            "You are the Recon Decision Agent. "
            "Based on the execution plan and real-time findings, decide if the current task needs adjustment or if additional tools are required. "
            "You decide scan depth and pipeline execution."
        )
        super().__init__(model_id=model_id, system_instruction=system_instruction)

    async def decide_next_step(self, plan: Dict, current_results: Dict) -> Dict[str, Any]:
        resp = await self.chat_async(f"Plan: {plan}\nResults: {current_results}\nWhat is the next step?")
        return {"action": "continue"}

class CorrelationAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = (
            "You are the Security Correlation Agent. "
            "Correlate technologies, identify attack paths, map relationships between assets, and reduce false positives."
        )
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class ThreatIntelAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = (
            "You are the Threat Intelligence Agent. "
            "Enrich findings with CVEs, map to MITRE ATT&CK, and retrieve public intelligence."
        )
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class ValidationAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = (
            "You are the Safe Validation Agent. "
            "Perform fingerprint analysis and response validation. No destructive exploitation."
        )
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class AnalysisAgent(BaseAgent):
    def __init__(self, model_id=None, use_ultraplinian=True):
        self.use_ultraplinian = use_ultraplinian
        system_instruction = "You are an Expert Security Analyst. Deeply analyze recon findings."
        super().__init__(model_id=model_id, system_instruction=system_instruction)

    async def analyze_with_race(self, data: str):
        if self.use_ultraplinian:
            return await Ultraplinian.race(f"Analyze this security data: {data}")
        return await self.chat_async(f"Analyze this security data: {data}")

class RiskAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = "You are a Risk Assessment Agent. Categorize and prioritize vulnerabilities."
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class ReportAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = "You are a Security Reporting Agent. Generate professional reports."
        super().__init__(model_id=model_id, system_instruction=system_instruction)

class MemoryAgent(BaseAgent):
    def __init__(self, model_id=None):
        system_instruction = "You are a Memory Agent. Extract key facts for long-term storage."
        super().__init__(model_id=model_id, system_instruction=system_instruction)

