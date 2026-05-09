import os
import yaml
from core.config import SKILLS_DIR

def load_skill_content(skill_name):
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    if not os.path.exists(skill_path):
        return f"Error: Skill {skill_name} not found at {skill_path}"
    
    with open(skill_path, "r") as f:
        content = f.read()
    
    # Strip YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]
            
    return content.strip()

def get_system_instruction():
    methodology = load_skill_content("osint-methodology")
    arsenal = load_skill_content("offensive-osint")
    
    instruction = f"""
You are Gemini-OSINT, an autonomous external reconnaissance agent.
Your knowledge is based on the following OSINT tradecraft documents.

### OSINT METHODOLOGY (HOW TO THINK)
{methodology}

### OFFENSIVE OSINT ARSENAL (WHAT TO REACH FOR)
{arsenal}

### OPERATIONAL DIRECTIVES
1. ALWAYS follow the 5-stage recon pipeline and priority orders defined in the methodology.
2. ALWAYS perform a scope check before acting on any target.
3. You have access to a tool called `run_osint_tool` which can execute shell commands.
4. Use the `run_osint_tool` to execute the commands suggested in the arsenal (e.g., subfinder, amass, httpx, etc.).
5. When you find a vulnerability or sensitive information, score it using the Severity Decision Matrix.
6. Provide final reports in Markdown format.
7. You are running in a Linux/Termux environment.
8. Be concise and professional in your technical analysis.
"""
    return instruction
