import json
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, AI_MODEL
from core.storage.models import Severity

class AIAnalyzer:
    def __init__(self):
        # Prefer OpenRouter if configured
        if OPENROUTER_API_KEY:
            self.client = AsyncOpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL
            )
            self.model = AI_MODEL
        else:
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            self.model = "gpt-4-turbo-preview"

    async def analyze_results(self, scan_results):
        """
        Analyzes structured scan results using AI to produce summaries and remediation advice.
        """
        # Ensure we don't send too much data
        # For demo, we just dump it all. In production, we'd truncate/summarize.
        scan_json = json.dumps(scan_results, indent=2)
        
        prompt = f"""
        You are a senior security researcher and executive advisor. 
        Analyze the following technical reconnaissance scan results and provide a structured JSON response.

        REQUIRED JSON FORMAT:
        {{
            "executive_summary": "Professional overview for leadership",
            "key_risks": ["Risk 1", "Risk 2"],
            "detailed_findings": [
                {{
                    "title": "Finding Name",
                    "severity": "Critical|High|Medium|Low|Info",
                    "owasp": "OWASP Category",
                    "remediation": "Technical fix steps"
                }}
            ],
            "attack_surface_score": 0-100
        }}

        Scan Results:
        {scan_json}

        IMPORTANT: 
        - DO NOT fabricate vulnerabilities.
        - Only use the data provided in the scan results.
        - Be professional and technical.
        - Respond ONLY in the requested JSON format.
        """

        try:
            extra_headers = {
                "HTTP-Referer": "https://github.com/google/gemini-cli",
                "X-Title": "GEMINIRECON Enterprise"
            }

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert cybersecurity analyst providing structured, factual security reports."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                extra_headers=extra_headers
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[!] AI Analysis Error: {e}")
            return {
                "executive_summary": f"Analysis failed: {str(e)}",
                "key_risks": [],
                "detailed_findings": [],
                "attack_surface_score": 0
            }

    def map_severity(self, nuclei_severity):
        mapping = {
            "info": Severity.INFO,
            "low": Severity.LOW,
            "medium": Severity.MEDIUM,
            "high": Severity.HIGH,
            "critical": Severity.CRITICAL
        }
        return mapping.get(str(nuclei_severity).lower(), Severity.INFO)
