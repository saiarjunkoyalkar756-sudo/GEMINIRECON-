# GEMINIRECON 🛡️

**AI-Powered Reconnaissance & Attack Surface Intelligence Platform**

GEMINIRECON is a next-generation modular framework designed for automated passive reconnaissance, attack surface mapping, and OSINT automation, powered by the **Google Gemini 2.0 API**.

![Banner](assets/banner.png)

## 🌟 Key Features

- **Multi-Agent Orchestration**: Specialized AI agents for planning, execution, analysis, and risk assessment.
- **Passive-First Recon**: Automated discovery of subdomains, DNS records, and technologies without active scanning by default.
- **AI-Driven Insights**: Deep analysis of recon data to identify high-value targets and interesting patterns.
- **Modular Plugin System**: Easily extendable with new recon tools and techniques.
- **Interactive TUI**: A professional terminal user interface built with Textual.
- **Persistent Memory**: SQLite-backed history tracking to monitor changes over time.
- **Professional Reporting**: Generate executive summaries and technical reports in Markdown/HTML.

## 🏗️ Architecture

GEMINIRECON uses a sophisticated multi-agent system:

1.  **Planner Agent**: Analyzes user goals and creates optimal recon workflows.
2.  **Recon Agent**: Executes tools and gathers raw data.
3.  **Analysis Agent**: Summarizes findings and extracts security-relevant metadata.
4.  **Risk Agent**: Prioritizes findings and assigns risk scores.
5.  **Report Agent**: Generates professional documentation.
6.  **Memory Agent**: Manages historical data and compares results.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Google Gemini API Key

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/username/GEMINIRECON.git
    cd GEMINIRECON
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure environment variables:
    ```bash
    cp .env.example .env
    # Edit .env and add your GEMINI_API_KEY
    ```

### Usage

Launch the interactive TUI:
```bash
python main.py
```

### API Mode

For headless operation or integration with the web frontend:
```bash
export PYTHONPATH=$PYTHONPATH:.
python api/server.py
```
The API will be available at `http://localhost:8000`.

### Web Dashboard & G0DM0D3

GEMINIRECON includes a Next.js-based web dashboard and the **G0DM0D3** liberated AI interface.

To start G0DM0D3:
```bash
cd G0DM0D3
npm install
npm run dev
```

## 🛠️ Supported Tools

- `subfinder`, `amass`, `httpx`, `whois`, `dig`, `dnsx`, `naabu`, `nuclei`, `gowitness`, `katana`, `wafw00f`
- *Note: These tools must be installed in your PATH.*

## 🐳 Docker Deployment

Run the entire stack with Docker:
```bash
docker-compose up --build
```

## 🛡️ Safety & Ethics

GEMINIRECON is designed for **authorized security research and defensive intelligence only**. It strictly enforces:
- Command whitelisting
- Passive reconnaissance by default
- User confirmation for active scans
- Detailed logging of all actions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed for professional cybersecurity portfolios and serious security research.*
