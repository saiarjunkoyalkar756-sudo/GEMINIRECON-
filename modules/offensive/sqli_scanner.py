import asyncio
import os
from scanners.base import BaseScanner

class SQLiScanner(BaseScanner):
    async def run(self):
        output_dir = os.path.join(self.output_dir, "sqli")
        os.makedirs(output_dir, exist_ok=True)
        # Using sqlmap for offensive discovery
        command = f"sqlmap -u {self.target} --batch --crawl=3 --output-dir={output_dir}"
        stdout, stderr, code = await self.execute_command(command)
        return {"status": "completed", "output_dir": output_dir}
