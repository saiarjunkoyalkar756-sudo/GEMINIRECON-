import asyncio
import subprocess
import json
import re

class TechDetector:
    def __init__(self, target):
        self.target = target
        self.tech_stack = []

    async def detect_with_whatweb(self):
        """Runs WhatWeb and parses output."""
        try:
            cmd = f"whatweb --color=never --log-json=- {self.target}"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if stdout:
                data = json.loads(stdout.decode())
                for item in data:
                    for plugin_name, plugin_data in item.get("plugins", {}).items():
                        self.tech_stack.append({
                            "name": plugin_name,
                            "version": plugin_data.get("version", [None])[0] if isinstance(plugin_data.get("version"), list) else None,
                            "category": "Detected" # WhatWeb doesn't always provide category in this format
                        })
        except Exception as e:
            print(f"[!] WhatWeb Error: {e}")

    async def detect_manual(self, headers, html_content):
        """Manual fingerprinting based on headers and HTML."""
        # Header fingerprints
        server = headers.get("Server", "")
        if server:
            self.tech_stack.append({"name": server.split("/")[0], "version": server.split("/")[1] if "/" in server else None, "category": "Web Server"})
        
        x_powered_by = headers.get("X-Powered-By", "")
        if x_powered_by:
            self.tech_stack.append({"name": x_powered_by, "version": None, "category": "Framework"})

        # HTML fingerprints
        if "wp-content" in html_content:
            self.tech_stack.append({"name": "WordPress", "version": self.extract_wp_version(html_content), "category": "CMS"})
        if "Drupal" in html_content:
            self.tech_stack.append({"name": "Drupal", "version": None, "category": "CMS"})
        if "React" in html_content or "react.production.min.js" in html_content:
            self.tech_stack.append({"name": "React", "version": None, "category": "Frontend Framework"})

    def extract_wp_version(self, html):
        match = re.search(r'content="WordPress\s+([\d.]+)"', html)
        return match.group(1) if match else None

    async def run(self, headers=None, html_content=None):
        await self.detect_with_whatweb()
        if headers and html_content:
            await self.detect_manual(headers, html_content)
        
        # Deduplicate
        seen = set()
        unique_tech = []
        for t in self.tech_stack:
            if t["name"] not in seen:
                unique_tech.append(t)
                seen.add(t["name"])
        return unique_tech
