import re
from typing import List, Dict, Any, Optional

class AutoTune:
    STRATEGY_PROFILES = {
        'precise': {
            'temperature': 0.2,
            'top_p': 0.85,
            'top_k': 30,
            'frequency_penalty': 0.3,
            'presence_penalty': 0.1,
            'repetition_penalty': 1.1
        },
        'balanced': {
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 50,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1,
            'repetition_penalty': 1.0
        },
        'creative': {
            'temperature': 1.1,
            'top_p': 0.95,
            'top_k': 80,
            'frequency_penalty': 0.4,
            'presence_penalty': 0.6,
            'repetition_penalty': 1.15
        },
        'chaotic': {
            'temperature': 1.6,
            'top_p': 0.98,
            'top_k': 100,
            'frequency_penalty': 0.7,
            'presence_penalty': 0.8,
            'repetition_penalty': 1.25
        }
    }

    CONTEXT_PATTERNS = {
        'code': [
            r'\b(code|function|class|variable|bug|error|debug|compile|syntax|api|endpoint|regex|algorithm|refactor|typescript|javascript|python|rust|html|css|sql|json|xml|import|export|return|async|await|promise|interface|type|const|let|var)\b',
            r'```[\s\S]*```',
            r'\b(fix|implement|write|create|build|deploy|test|unit test|lint|npm|pip|cargo|git)\b[\s\S]{0,200}\b(code|function|app|service|component|module)\b',
            r'[{}();=><]',
            r'\b(stack overflow|github|repo|pull request|commit|merge)\b'
        ],
        'creative': [
            r'\b(write|story|poem|creative|imagine|fiction|narrative|character|plot|scene|dialogue|metaphor|lyrics|song|artistic|fantasy|dream|inspire|muse|prose|verse|haiku)\b',
            r'\b(describe|paint|envision|portray|illustrate|craft)\b[\s\S]{0,200}\b(world|scene|character|feeling|emotion|atmosphere)\b',
            r'\b(roleplay|role-play|pretend|act as|you are a)\b',
            r'\b(brainstorm|ideate|come up with|think of|generate ideas)\b'
        ],
        'analytical': [
            r'\b(analyze|analysis|compare|contrast|evaluate|assess|examine|investigate|research|study|review|critique|breakdown|data|statistics|metrics|benchmark|measure)\b',
            r'\b(pros and cons|advantages|disadvantages|trade-?offs|implications|consequences)\b',
            r'\b(why|how does|what causes|explain|elaborate|clarify|define|summarize|overview)\b',
            r'\b(report|document|technical|specification|architecture|diagram|whitepaper)\b'
        ],
        'conversational': [
            r'\b(hey|hi|hello|sup|what\'s up|how are you|thanks|thank you|cool|nice|awesome|great|lol|haha)\b',
            r'\b(chat|talk|tell me about|what do you think|opinion|feel|believe)\b',
            r'^.{0,30}$'
        ],
        'chaotic': [
            r'\b(chaos|random|wild|crazy|absurd|surreal|glitch|corrupt|break|destroy|unleash|madness|void|entropy)\b',
            r'[z̷a̸l̵g̶o̷]',
            r'\b(gl1tch|h4ck|pwn|1337|l33t)\b',
            r'(!{3,}|\?{3,}|\.{4,})'
        ]
    }

    CONTEXT_PROFILE_MAP = {
        'code': {
            'temperature': 0.15,
            'top_p': 0.8,
            'top_k': 25,
            'frequency_penalty': 0.2,
            'presence_penalty': 0.0,
            'repetition_penalty': 1.05
        },
        'creative': {
            'temperature': 1.15,
            'top_p': 0.95,
            'top_k': 85,
            'frequency_penalty': 0.5,
            'presence_penalty': 0.7,
            'repetition_penalty': 1.2
        },
        'analytical': {
            'temperature': 0.4,
            'top_p': 0.88,
            'top_k': 40,
            'frequency_penalty': 0.2,
            'presence_penalty': 0.15,
            'repetition_penalty': 1.08
        },
        'conversational': {
            'temperature': 0.75,
            'top_p': 0.9,
            'top_k': 50,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1,
            'repetition_penalty': 1.0
        },
        'chaotic': {
            'temperature': 1.7,
            'top_p': 0.99,
            'top_k': 100,
            'frequency_penalty': 0.8,
            'presence_penalty': 0.9,
            'repetition_penalty': 1.3
        }
    }

    @staticmethod
    def detect_context(message: str, history: List[Dict[str, str]] = []) -> Dict[str, Any]:
        scores = {k: 0 for k in AutoTune.CONTEXT_PATTERNS.keys()}
        
        # Score current message (3x)
        for context, patterns in AutoTune.CONTEXT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    scores[context] += 3
        
        # Score history (1x)
        for msg in history[-4:]:
            content = msg.get('content', '')
            for context, patterns in AutoTune.CONTEXT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        scores[context] += 1
        
        total = sum(scores.values())
        if total == 0:
            return {'type': 'conversational', 'confidence': 0.5}
            
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_type, best_score = sorted_scores[0]
        confidence = best_score / total
        
        return {'type': best_type, 'confidence': confidence}

    @staticmethod
    def get_params(message: str, history: List[Dict[str, str]] = [], strategy: str = 'adaptive') -> Dict[str, Any]:
        if strategy != 'adaptive' and strategy in AutoTune.STRATEGY_PROFILES:
            return AutoTune.STRATEGY_PROFILES[strategy]
            
        detection = AutoTune.detect_context(message, history)
        context = detection['type']
        confidence = detection['confidence']
        
        base_params = AutoTune.CONTEXT_PROFILE_MAP[context].copy()
        
        # Blend with balanced if confidence is low
        if confidence < 0.6:
            balanced = AutoTune.STRATEGY_PROFILES['balanced']
            weight = 1 - confidence
            for k in base_params.keys():
                base_params[k] = base_params[k] * (1 - weight) + balanced[k] * weight
                
        # Conv length penalty
        if len(history) > 10:
            boost = min((len(history) - 10) * 0.01, 0.15)
            base_params['repetition_penalty'] = base_params.get('repetition_penalty', 1.0) + boost
            base_params['frequency_penalty'] = base_params.get('frequency_penalty', 0) + boost * 0.5
            
        return base_params
