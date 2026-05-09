import httpx
import asyncio

class CVEEngine:
    def __init__(self):
        self.api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    async def get_cves_for_tech(self, tech_name, version=None):
        """
        Queries NVD for CVEs related to a specific technology and version.
        Note: In a production environment, you should use an API key and handle rate limits.
        """
        if not version:
            return []

        cves = []
        try:
            # Simplified query for demonstration
            query = f"{tech_name} {version}"
            async with httpx.AsyncClient() as client:
                # This is a placeholder for the actual NVD API call which requires specific parameters
                # For this demo, we'll return a mock CVE if version is old
                if tech_name.lower() == "wordpress" and version < "6.0":
                    cves.append({
                        "cve_id": "CVE-2022-1234",
                        "cvss_score": 7.5,
                        "severity": "HIGH",
                        "description": f"Vulnerability in {tech_name} version {version} allowing XSS.",
                        "exploit_available": True
                    })
                elif tech_name.lower() == "apache" and version < "2.4.50":
                    cves.append({
                        "cve_id": "CVE-2021-41773",
                        "cvss_score": 9.8,
                        "severity": "CRITICAL",
                        "description": "Path traversal and remote code execution in Apache HTTP Server 2.4.49.",
                        "exploit_available": True
                    })
        except Exception as e:
            print(f"[!] CVE Engine Error: {e}")
        
        return cves

    async def correlate(self, tech_stack):
        correlated_results = []
        for tech in tech_stack:
            cves = await self.get_cves_for_tech(tech["name"], tech["version"])
            if cves:
                tech["cves"] = cves
                correlated_results.append(tech)
        return correlated_results
