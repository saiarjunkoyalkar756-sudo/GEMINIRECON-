import os
import re
from typing import Optional

# API key (set in Codespaces .env.local or environment)
API_KEY = os.getenv("SCANNER_API_KEY", "changeme")

# Execution timeouts (seconds)
SUBFINDER_TIMEOUT = 60
HTTPX_TIMEOUT = 60
NUCLEI_TIMEOUT = 120
NAABU_TIMEOUT = 60
NMAP_TIMEOUT = 120

# Nuclei default optimizations for low-resource environments
NUCLEI_CONCURRENCY = int(os.getenv("NUCLEI_CONCURRENCY", "5"))
NUCLEI_RATE_LIMIT = int(os.getenv("NUCLEI_RATE_LIMIT", "100"))
NUCLEI_BATCH_SIZE = int(os.getenv("NUCLEI_BATCH_SIZE", "25"))

# Rate limiting per API key (requests per WINDOW seconds)
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "10"))

# Allowed target regex (FQDN or IPv4)
FQDN_REGEX = re.compile(r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$")
IPV4_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

# Paths for tools (assumes GOPATH/bin in PATH)
SUBFINDER_BIN = os.getenv("SUBFINDER_BIN", "subfinder")
HTTPX_BIN = os.getenv("HTTPX_BIN", "httpx")
NUCLEI_BIN = os.getenv("NUCLEI_BIN", "nuclei")
NAABU_BIN = os.getenv("NAABU_BIN", "naabu")
NMAP_BIN = os.getenv("NMAP_BIN", "nmap")

# Other
WORK_DIR = os.getenv("WORK_DIR", "/workspace")

