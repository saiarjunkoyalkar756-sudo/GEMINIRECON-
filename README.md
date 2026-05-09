# GEMINIRECON 2.0 - Enterprise AI Recon & CVE Intelligence

GEMINIRECON is a production-grade attack surface management platform that combines high-performance reconnaissance tools with AI-driven intelligence and CVE correlation.

## 🌟 Enterprise Capabilities

- **Advanced Web Intelligence:** Async crawling, header analysis, and cookie auditing.
- **Technology Fingerprinting:** Deep detection of CMS, frameworks, and servers using WhatWeb and custom signatures.
- **CVE Correlation Engine:** Automatically matches detected technologies and versions with the NVD database.
- **JS Analysis Engine:** Scans JavaScript files for exposed API keys, secrets, and internal endpoints.
- **AI Analysis Engine:** Professionally summarizes REAL scan data into executive reports without hallucinations using OpenAI or OpenRouter.
- **Live Monitoring:** Real-time log streaming via WebSockets directly to the dashboard.
- **Scalable Architecture:** Built on FastAPI (Async) for high-concurrency enterprise environments.

## 🚀 Commands

Perform various levels of assessment via the CLI:

```bash
# Full comprehensive reconnaissance
python main.py --target https://example.com --full-recon

# Specific assessments
python main.py --target https://example.com --web-fetch
python main.py --target https://example.com --tech-detect
python main.py --target https://example.com --cve-scan
python main.py --target https://example.com --js-analysis
```

## 🛠️ Architecture

- **Backend:** FastAPI (Async), SQLite/PostgreSQL, BackgroundTasks.
- **Modules:** `WebFetchEngine`, `TechDetector`, `CVEEngine`, `JSAnalyzer`.
- **Scanners:** Subfinder, Nmap, Nuclei, WhatWeb.
- **Frontend:** React 18, TailwindCSS, Recharts, Lucide.

## 📦 Deployment

1. **Setup:** `./setup.sh`
2. **Configure:** Update `.env` with `OPENAI_API_KEY`.
3. **Run:** `docker-compose up -d`

---
*Built for Security Engineers, Bug Hunters, and SOC Teams.*
