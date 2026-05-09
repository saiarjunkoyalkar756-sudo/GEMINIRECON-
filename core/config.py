import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
AGENTS_DIR = BASE_DIR / "agents"
PLUGINS_DIR = BASE_DIR / "plugins"
STORAGE_DIR = BASE_DIR / "storage"
REPORTS_DIR = BASE_DIR / "reports"
PROMPTS_DIR = BASE_DIR / "prompts"

# Ensure directories exist
for dist in [STORAGE_DIR, REPORTS_DIR, PLUGINS_DIR]:
    dist.mkdir(exist_ok=True)

# API Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash") # Defaulting to 2.0-flash as per update.txt

# Tool Settings
TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "300"))

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{STORAGE_DIR}/recon.db")

# Command Whitelist
ALLOWED_COMMANDS = [
    "subfinder", "amass", "httpx", "whois", "dig", "nmap", 
    "curl", "python3", "grep", "awk", "sed", "sort", 
    "uniq", "cat", "head", "tail", "wc", "dnsx", "naabu",
    "nuclei", "gowitness", "katana", "wafw00f"
]

# Safety Settings
PASSIVE_MODE_DEFAULT = True
REQUIRE_CONFIRMATION_FOR_ACTIVE = True
MAX_RECURSION_DEPTH = 3
