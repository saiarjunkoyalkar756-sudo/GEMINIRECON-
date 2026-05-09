import asyncio
import os
import json
import hashlib
from scanners.base import BaseScanner

class AdvancedOffensiveScanner(BaseScanner):
    def __init__(self, target, scan_job_id, tool_name):
        super().__init__(target, scan_job_id)
        self.tool_name = tool_name

    async def save_unique_finding(self, finding_data):
        """Deduplicates findings using a hash."""
        finding_hash = hashlib.sha256(json.dumps(finding_data, sort_keys=True).encode()).hexdigest()
        # In a real app, check DB for existence here
        return finding_hash

class FFufScanner(AdvancedOffensiveScanner):
    def __init__(self, target, scan_job_id):
        super().__init__(target, scan_job_id, "ffuf")
    
    async def run(self):
        # Automated Fuzzing with intelligent filtering
        wordlist = "/usr/share/wordlists/dirb/common.txt"
        output_file = os.path.join(self.output_dir, "fuzzing.json")
        command = f"ffuf -u {self.target}/FUZZ -w {wordlist} -mc 200,204,301,302,403 -of json -o {output_file}"
        return await self.execute_command(command)
