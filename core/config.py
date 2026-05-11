import os
from dotenv import load_dotenv

load_dotenv()

# Project Info
PROJECT_NAME = "GEMINIRECON"
VERSION = "2.0.0"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./geminirecon.db")

# Redis & Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

# AI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_KEY = GOOGLE_API_KEY # Alias for convenience
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini") # "gemini" or "openrouter"

AI_MODEL = os.getenv("AI_MODEL", OPENROUTER_MODEL if LLM_PROVIDER == "openrouter" else GEMINI_MODEL)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "recon-artifacts")

# Upstash Vector Configuration
UPSTASH_VECTOR_REST_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_VECTOR_REST_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

# Scanning Constants
MAX_PARALLEL_SCANS = 5
SCAN_TIMEOUT = 3600 # 1 hour

# File Paths
RESULTS_DIR = os.path.join(os.getcwd(), "results")
REPORTS_DIR = os.path.join(os.getcwd(), "reports")

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
