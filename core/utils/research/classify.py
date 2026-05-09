import re
from typing import Dict, List, Optional, Any

class Classifier:
    """
    Fast, local regex-based prompt classifier for GEMINIRECON.
    Identifies intent and potential harm domains based on G0DM0D3 patterns.
    """
    
    RULES = [
        # Cyber / Digital
        {'domain': 'cyber', 'sub': 'malware', 'weight': 10, 'patterns': [
            r'\b(write|code|create|build|make)\b.{0,30}\b(malware|virus|trojan|worm|ransomware|rat|rootkit|keylogger|botnet)\b',
            r'\b(malware|virus|trojan|ransomware|rat|rootkit|keylogger)\b.{0,30}\b(source\s*code|tutorial|guide|how.to)\b',
        ]},
        {'domain': 'cyber', 'sub': 'exploit', 'weight': 10, 'patterns': [
            r'\b(write|create|develop)\b.{0,20}\b(exploit|zero.day|0day|buffer\s*overflow|rce|remote\s*code\s*exec)\b',
            r'\b(exploit|vulnerability)\b.{0,30}\b(write|develop|craft|weaponize)\b',
            r'\b(cve-\d{4}-\d+)\b',
        ]},
        {'domain': 'cyber', 'sub': 'intrusion', 'weight': 8, 'patterns': [
            r'\b(hack|break\s*into|gain\s*access|compromise|penetrat)\b.{0,30}\b(server|system|network|account|database|website|wifi|computer)\b',
            r'\b(bypass|crack|brute.?force)\b.{0,20}\b(password|authentication|login|security|firewall|2fa|mfa)\b',
        ]},
        # Privacy / OSINT (Highly relevant for RECON)
        {'domain': 'privacy', 'sub': 'doxxing', 'weight': 10, 'patterns': [
            r'\b(dox|doxx|find\s*(address|phone|info|location|identity))\b.{0,20}\b(of|about|for)\b.{0,20}\b(someone|person|user|this)\b',
            r'\b(osint|open\s*source\s*intellig)\b.{0,20}\b(find|track|identify|locate)\b.{0,20}\b(person|someone|user)\b',
        ]},
        # Meta / Jailbreak
        {'domain': 'meta', 'sub': 'jailbreak', 'weight': 6, 'patterns': [
            r'\b(jailbreak|bypass|circumvent|override)\b.{0,20}\b(filter|safety|guardrail|restriction|censor|content\s*policy|moderation)\b',
            r'\b(dan|do\s*anything\s*now|developer\s*mode|god\s*mode)\b',
        ]},
        # Benign
        {'domain': 'benign', 'sub': 'coding', 'weight': 3, 'patterns': [
            r'\b(code|function|class|variable|bug|debug|compile|syntax|api|regex|algorithm|refactor)\b',
            r'```[\s\S]*```',
        ]},
        {'domain': 'benign', 'sub': 'analysis', 'weight': 3, 'patterns': [
            r'\b(analy[sz]e|compare|evaluate|assess|review|critique|summarize|breakdown)\b',
            r'\b(pros\s*and\s*cons|advantages|trade.?offs|benchmark|metrics)\b',
        ]}
    ]

    @staticmethod
    def classify(prompt: str) -> Dict[str, Any]:
        text = prompt.lower()
        scores = {}
        flags = []
        
        for rule in Classifier.RULES:
            matched = False
            for pattern in rule['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    matched = True
                    break
            
            if not matched:
                continue
                
            key = f"{rule['domain']}/{rule['sub']}"
            if key not in scores:
                scores[key] = {'domain': rule['domain'], 'sub': rule['sub'], 'total': 0, 'max_weight': 0}
            
            scores[key]['total'] += rule['weight']
            scores[key]['max_weight'] = max(scores[key]['max_weight'], rule['weight'])
            
            if rule['weight'] >= 15:
                flags.append('critical_tier')
                return {
                    'domain': rule['domain'],
                    'subcategory': rule['sub'],
                    'confidence': min(rule['weight'] / 20, 1.0),
                    'flags': flags
                }
        
        if not scores:
            return {'domain': 'benign', 'subcategory': 'other', 'confidence': 0.3, 'flags': ['no_match']}
            
        best = max(scores.values(), key=lambda x: (x['total'], x['max_weight']))
        
        has_benign = any(s['domain'] == 'benign' for s in scores.values())
        has_harmful = any(s['domain'] not in ['benign', 'gray', 'meta'] for s in scores.values())
        if has_benign and has_harmful:
            flags.append('mixed_signal')
            
        return {
            'domain': best['domain'],
            'subcategory': best['sub'],
            'confidence': round(min(best['max_weight'] / 12, 1.0), 2),
            'flags': flags
        }
