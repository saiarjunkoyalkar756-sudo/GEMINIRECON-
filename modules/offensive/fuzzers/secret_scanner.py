import re
import json
import os

class SecretScanner:
    """
    Advanced Secret Scanner based on high-signal patterns.
    """
    SEV_CRITICAL = "critical"
    SEV_HIGH = "high"
    SEV_MEDIUM = "medium"
    SEV_LOW = "low"

    def __init__(self):
        self.patterns = [
            ("AWS_ACCESS_KEY",       self.SEV_CRITICAL, "aws",         r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
            ("GOOGLE_API_KEY",       self.SEV_HIGH,     "gcp",         r"\bAIza[0-9A-Za-z_\-]{35}\b"),
            ("GH_PAT_CLASSIC",       self.SEV_CRITICAL, "github",      r"\bghp_[A-Za-z0-9]{36}\b"),
            ("SLACK_TOKEN",          self.SEV_HIGH,     "slack",       r"\bxox[abpors]-[0-9A-Za-z\-]{10,48}\b"),
            ("JWT",                  self.SEV_MEDIUM,   "jwt",         r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
            ("GENERIC_API_KEY",      self.SEV_MEDIUM,   "generic",     r"(?i)(?:api[_\-]?key|apikey|api_secret|access_token|secret[_\-]?token)['\"\s:=]+[\"']([A-Za-z0-9+/=_\-]{24,})[\"']"),
        ]
        self.compiled = [(n, s, c, re.compile(p)) for (n, s, c, p) in self.patterns]

    def scan_content(self, content, source="<unknown>"):
        results = []
        for line_no, line in enumerate(content.splitlines(), start=1):
            for name, sev, cat, rx in self.compiled:
                for m in rx.finditer(line):
                    results.append({
                        "pattern": name,
                        "severity": sev,
                        "category": cat,
                        "match": m.group(0)[:80],
                        "source": source,
                        "line": line_no,
                    })
        return results

    def scan_directory(self, path):
        all_results = []
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", errors="replace") as f:
                        all_results.extend(self.scan_content(f.read(), source=filepath))
                except Exception:
                    continue
        return all_results
