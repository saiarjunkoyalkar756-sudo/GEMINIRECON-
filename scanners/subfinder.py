from scanners.base import BaseScanner
import os

class SubfinderScanner(BaseScanner):
    async def run(self):
        output_file = os.path.join(self.output_dir, "subdomains.txt")
        command = f"subfinder -d {self.target} -o {output_file}"
        stdout, stderr, code = await self.execute_command(command)
        
        subdomains = []
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                subdomains = [line.strip() for line in f if line.strip()]
        
        return subdomains
