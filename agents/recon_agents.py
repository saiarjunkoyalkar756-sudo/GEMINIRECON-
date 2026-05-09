from agents.base_agent import BaseAgent
from tools.runner import ToolRunner
import asyncio
import os

class SubdomainAgent(BaseAgent):
    async def run(self, target):
        # Recursive enumeration using subfinder + assetfinder
        await ToolRunner.run("subfinder", target, args=f"-d {target} -o results/{target}/subdomains.txt")
        return {"agent": "SubdomainAgent", "status": "done"}

class ScreenshotAgent(BaseAgent):
    async def run(self, target):
        # Ensure we have live hosts for gowitness
        await ToolRunner.run("httpx", target, args=f"-l results/{target}/subdomains.txt -o results/{target}/alive.txt")
        # Screenshotting alive hosts
        result = await ToolRunner.run("gowitness", target, args=f"file -f results/{target}/alive.txt --destination results/{target}/screenshots/")
        return {"agent": "ScreenshotAgent", "status": "done"}

class VulnerabilityAgent(BaseAgent):
    async def run(self, target):
        # 1. Directory Fuzzing
        await ToolRunner.run("ffuf", target, args=f"-w /usr/share/wordlists/dirb/common.txt -u http://FUZZ.{target} -o results/{target}/fuzz.json")
        # 2. Nuclei Scan
        result = await ToolRunner.run("nuclei", target, args=f"-l results/{target}/alive.txt -o results/{target}/vulnerabilities.json")
        return {"agent": "VulnerabilityAgent", "status": "done"}

class ExploitAgent(BaseAgent):
    async def run_sqli(self, url):
        # Active exploitation only if requested
        result = await ToolRunner.run("sqlmap", url, args=f"-u {url} --batch --crawl=2")
        return {"agent": "ExploitAgent", "type": "SQLi", "data": result}
