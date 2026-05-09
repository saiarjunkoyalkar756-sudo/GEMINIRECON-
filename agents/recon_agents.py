from agents.base_agent import BaseAgent
from tools.runner import ToolRunner

class SubdomainAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction="You are a subdomain enumeration expert.")
        
    async def run(self, target):
        # Execute tool via runner
        result = await ToolRunner.run("subfinder", f"-d {target}")
        return {"agent": "SubdomainAgent", "data": result}

class PortScanAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction="You are a port scanning expert.")
        
    async def run(self, target):
        result = await ToolRunner.run("naabu", f"-host {target}")
        return {"agent": "PortScanAgent", "data": result}

class VulnerabilityAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction="You are a vulnerability scanning expert.")
        
    async def run(self, target):
        result = await ToolRunner.run("nuclei", f"-target {target}")
        return {"agent": "VulnerabilityAgent", "data": result}

class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(system_instruction="You are a security report generation expert.")
        
    async def generate(self, target, data):
        # Logic to compile final markdown report
        return f"Report generated for {target}"
