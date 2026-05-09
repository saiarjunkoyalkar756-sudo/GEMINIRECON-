import argparse
import asyncio
import httpx
import json
import sys
from core.config import PROJECT_NAME, VERSION

API_URL = "http://localhost:8000/scans/"

async def trigger_scan(target, options):
    print(f"[*] Initializing GEMINIRECON {VERSION}")
    print(f"[*] Target: {target}")
    
    payload = {
        "target_url": target,
        "options": options
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(API_URL, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                print(f"[+] Scan successfully queued. ID: {data['scan_id']}")
                return data['scan_id']
            else:
                print(f"[!] Error: {resp.text}")
        except Exception as e:
            print(f"[!] Connection failed: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} - Enterprise AI Recon Platform")
    parser.add_argument("--target", required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument("--full-recon", action="store_true", help="Perform comprehensive reconnaissance")
    parser.add_argument("--web-fetch", action="store_true", help="Fetch and analyze web intelligence")
    parser.add_argument("--cve-scan", action="store_true", help="Correlate technologies with CVEs")
    parser.add_argument("--js-analysis", action="store_true", help="Analyze JS files for secrets")
    parser.add_argument("--tech-detect", action="store_true", help="Identify technology stack")
    
    args = parser.parse_args()
    
    options = {
        "full_recon": args.full_recon,
        "web_fetch": args.web_fetch,
        "cve_scan": args.cve_scan,
        "js_analysis": args.js_analysis,
        "tech_detect": args.tech_detect
    }
    
    # In a real scenario, we might want to watch the logs here
    asyncio.run(trigger_scan(args.target, options))

if __name__ == "__main__":
    main()
