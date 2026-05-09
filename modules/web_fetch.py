import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class WebFetchEngine:
    def __init__(self, target_url, rate_limit=2, timeout=10):
        self.target_url = target_url
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.visited_urls = set()
        self.results = {
            "endpoints": [],
            "js_files": [],
            "headers": {},
            "cookies": [],
            "security_headers": {},
            "tech_hints": [],
            "forms": [],
            "admin_panels": [],
            "exposed_files": []
        }
        self.client = httpx.AsyncClient(
            follow_redirects=True, 
            timeout=self.timeout,
            verify=False,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GEMINIRECON/2.0"}
        )

    async def fetch(self, url):
        if url in self.visited_urls:
            return None
        self.visited_urls.add(url)
        
        try:
            response = await self.client.get(url)
            return response
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
            return None

    async def analyze_response(self, response):
        if not response:
            return

        url = str(response.url)
        self.results["endpoints"].append({
            "url": url,
            "status": response.status_code,
            "length": len(response.content)
        })

        # Headers Analysis
        headers = dict(response.headers)
        self.results["headers"] = headers
        
        # Security Headers Check
        sec_headers = ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security"]
        for sh in sec_headers:
            self.results["security_headers"][sh] = headers.get(sh, "MISSING")

        # Cookies
        for name, value in response.cookies.items():
            self.results["cookies"].append({
                "name": name,
                "value": value
            })

        # Content Analysis
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract JS
        for script in soup.find_all('script'):
            src = script.get('src')
            if src:
                full_src = urljoin(url, src)
                self.results["js_files"].append(full_src)

        # Extract Forms
        for form in soup.find_all('form'):
            action = form.get('action')
            method = form.get('method', 'get').upper()
            self.results["forms"].append({"action": action, "method": method})

        # Sensitive Path Detection (Regex)
        patterns = {
            "admin_panel": r"(admin|login|dashboard|panel|manage)",
            "exposed_file": r"(\.env|\.git|\.config|config\.php|web\.config|phpinfo)",
            "api_endpoint": r"/api/v[0-9]/"
        }
        
        for key, pattern in patterns.items():
            if re.search(pattern, url, re.I):
                if key == "admin_panel": self.results["admin_panels"].append(url)
                if key == "exposed_file": self.results["exposed_files"].append(url)

    async def run(self, max_pages=10):
        response = await self.fetch(self.target_url)
        if response:
            await self.analyze_response(response)
            
            # Simple crawling (limited for now)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [urljoin(self.target_url, a.get('href')) for a in soup.find_all('a', href=True)]
            
            tasks = []
            count = 0
            for link in links:
                if urlparse(link).netloc == urlparse(self.target_url).netloc and count < max_pages:
                    tasks.append(self.fetch_and_analyze(link))
                    count += 1
            
            await asyncio.gather(*tasks)
        
        await self.client.aclose()
        return self.results

    async def fetch_and_analyze(self, url):
        resp = await self.fetch(url)
        if resp:
            await self.analyze_response(resp)
