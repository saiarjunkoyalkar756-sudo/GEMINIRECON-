import subprocess
import shlex
import asyncio
from core.config import ALLOWED_COMMANDS, TOOL_TIMEOUT

# Global callback registry for tool execution updates
_tool_callback = None

def set_tool_callback(callback):
    global _tool_callback
    _tool_callback = callback

async def execute_command(command_str):
    """
    Safely executes a shell command if it's in the whitelist.
    """
    try:
        # Split command to extract the base utility
        parts = shlex.split(command_str)
        if not parts:
            return "Error: Empty command string"
        
        base_cmd = parts[0]
        
        # Check against whitelist
        if base_cmd not in ALLOWED_COMMANDS:
            return f"Error: Command '{base_cmd}' is not in the allowed whitelist."
        
        if _tool_callback:
            if asyncio.iscoroutinefunction(_tool_callback):
                await _tool_callback(f"Running tool: {command_str}")
            else:
                _tool_callback(f"Running tool: {command_str}")

        # Execute the command
        process = await asyncio.create_subprocess_exec(
            *parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=TOOL_TIMEOUT)
            
            output = stdout.decode()
            if stderr:
                output += "\n--- STDERR ---\n" + stderr.decode()
                
            return output if output else "(Command completed with no output)"
        except asyncio.TimeoutExpired:
            process.kill()
            return f"Error: Command timed out after {TOOL_TIMEOUT} seconds."
        
    except Exception as e:
        return f"Error executing command: {str(e)}"

def run_osint_tool(command: str) -> str:
    """
    Execute an OSINT tool command on the system.
    
    Args:
        command: The full command string to execute (e.g., 'subfinder -d example.com')
        
    Returns:
        The STDOUT and STDERR of the command.
    """
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # If we are in the main thread (unlikely for Gemini tool calls in this setup)
            # or in a thread that has a running loop.
            # We use run_coroutine_threadsafe to run it on the main loop if that's where set_tool_callback was called.
            # Actually, _tool_callback is usually the FastAPI main loop's broadcast.
            
            # Use the current loop to run the command
            future = asyncio.run_coroutine_threadsafe(execute_command(command), loop)
            return future.result()
        else:
            return loop.run_until_complete(execute_command(command))
    except Exception as e:
        return f"Error in tool wrapper: {str(e)}"
