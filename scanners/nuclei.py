from scanners.base import BaseScanner
import os
import json

class NucleiScanner(BaseScanner):
    async def run(self):
        output_file = os.path.join(self.output_dir, "nuclei.json")
        # Run nuclei with JSON output, optimized for lower memory (-bulk-size 5)
        command = f"nuclei -u {self.target} -json -no-update -bulk-size 5 -o {output_file}"
        stdout, stderr, code = await self.execute_command(command)
        
        results = []
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                for line in f:
                    try:
                        results.append(json.loads(line))
                    except:
                        continue
        
        return results
