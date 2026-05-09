import asyncio
import os
import json
from abc import ABC, abstractmethod
from core.config import RESULTS_DIR

class BaseScanner(ABC):
    def __init__(self, target, scan_job_id):
        self.target = target
        self.scan_job_id = scan_job_id
        self.output_dir = os.path.join(RESULTS_DIR, str(scan_job_id))
        os.makedirs(self.output_dir, exist_ok=True)

    @abstractmethod
    async def run(self):
        pass

    async def execute_command(self, command):
        """Safely execute a shell command and capture output."""
        print(f"[*] Executing: {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode
