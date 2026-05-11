import asyncio
import os
import shlex
import logging
from typing import Dict, Any, Optional
from tools.registry import registry
from datetime import datetime
from storage.cloud import storage as cloud_storage

logger = logging.getLogger(__name__)

class ExecutionEngine:
    def __init__(self, results_base_dir: str = "results"):
        self.results_base_dir = results_base_dir
        os.makedirs(self.results_base_dir, exist_ok=True)

    async def execute_tool(self, tool_name: str, params: Dict[str, Any], target_id: Optional[str] = None) -> Dict[str, Any]:
        tool_def = registry.get_tool(tool_name)
        if not tool_def:
            return {"status": "error", "message": f"Tool '{tool_name}' not found in registry"}

        # Prepare command
        try:
            # Fill in defaults
            full_params = {}
            for param in tool_def.parameters:
                full_params[param.name] = params.get(param.name, param.default)
            
            command = tool_def.command_template.format(**full_params)
        except KeyError as e:
            return {"status": "error", "message": f"Missing required parameter: {str(e)}"}

        # Setup output directory
        target_dir = target_id or "default"
        output_dir = os.path.join(self.results_base_dir, target_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{tool_name}_{timestamp}.log")

        logger.info(f"Executing: {command}")
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Save output
            with open(output_file, "wb") as f:
                f.write(stdout)
                if stderr:
                    f.write(b"\n--- STDERR ---\n")
                    f.write(stderr)

            # Upload to cloud storage if enabled
            cloud_url = await cloud_storage.upload_file(output_file, f"{target_dir}/{os.path.basename(output_file)}")

            return {
                "status": "success" if process.returncode == 0 else "failed",
                "return_code": process.returncode,
                "stdout": stdout.decode(errors="replace"),
                "stderr": stderr.decode(errors="replace"),
                "output_file": output_file,
                "cloud_url": cloud_url
            }

        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Global engine instance
execution_engine = ExecutionEngine()
