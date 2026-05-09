import asyncio
import httpx
import re

class JSAnalyzer:
    def __init__(self, js_urls):
        self.js_urls = js_urls
        self.results = []
        self.patterns = {
            "google_api": r"AIza[0-9A-Za-z-_]{35}",
            "firebase": r"firebaseio\.com",
            "slack_token": r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}",
            "aws_key": r"AKIA[0-9A-Z]{16}",
            "jwt": r"eyJh[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
            "endpoint": r"\"(https?://[^\"]+)\"|'([^\']+)'",
            "internal_ip": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        }

    async def analyze_url(self, url):
        try:
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    content = resp.text
                    findings = []
                    for key, pattern in self.patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            findings.append({"type": key, "matches": list(set(matches))[:10]})
                    
                    if findings:
                        return {"url": url, "findings": findings}
        except Exception as e:
            print(f"[!] JS Analysis Error for {url}: {e}")
        return None

    async def run(self):
        tasks = [self.analyze_url(url) for url in self.js_urls]
        results = await asyncio.gather(*tasks)
        self.results = [r for r in results if r]
        return self.results
