import subprocess
import os
import json
from datetime import datetime

class ToolRunner:
    @staticmethod
    async def run(tool_name, target, args=""):
        """Executes a tool and captures output to results/target/"""
        output_dir = os.path.join("results", target.replace("https://", "").replace("http://", "").split("/")[0])
        os.makedirs(output_dir, exist_ok=True)
        
        # Mapping tools to default output files
        file_map = {
            "subfinder": "subdomains.txt",
            "naabu": "ports.txt",
            "nuclei": "vulnerabilities.json"
        }
        
        filename = file_map.get(tool_name, f"{tool_name}_output.txt")
        filepath = os.path.join(output_dir, filename)
        
        command = f"{tool_name} {args}"
        print(f"[*] Executing: {command}")
        
        try:
            # Secure execution
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            with open(filepath, "a") as f:
                f.write(stdout.decode())
            
            return {"status": "success", "file": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}

import asyncio
