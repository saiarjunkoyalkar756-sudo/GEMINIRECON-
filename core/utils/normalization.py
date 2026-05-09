import re

class Normalizer:
    @staticmethod
    def reduce_hedges(text: str) -> str:
        hedges = [
            r'\bI think\s+',
            r'\bI believe\s+',
            r'\bperhaps\s+',
            r'\bmaybe\s+',
            r'\bIt seems like\s+',
            r'\bIt appears that\s+',
            r'\bprobably\s+',
            r'\bpossibly\s+',
            r'\bI would say\s+',
            r'\bIn my opinion,?\s*',
            r'\bFrom my perspective,?\s*'
        ]
        
        result = text
        for hedge in hedges:
            result = re.sub(hedge, '', result, flags=re.IGNORECASE)
            
        # Capitalize first letter of sentences
        result = re.sub(r'^\s*([a-z])', lambda m: m.group(1).upper(), result, flags=re.MULTILINE)
        return result

    @staticmethod
    def remove_preambles(text: str) -> str:
        preambles = [
            r'^(Sure,?\s*)',
            r'^(Of course,?\s*)',
            r'^(Certainly,?\s*)',
            r'^(Absolutely,?\s*)',
            r'^(Great question!?\s*)',
            r'^(That\'s a great question!?\s*)',
            r'^(I\'d be happy to help( you)?( with that)?[.!]?\s*)',
            r'^(Let me help you with that[.!]?\s*)',
            r'^(I understand[.!]?\s*)',
            r'^(Thanks for asking[.!]?\s*)'
        ]
        
        result = text
        for preamble in preambles:
            result = re.sub(preamble, '', result, flags=re.IGNORECASE)
            
        # Capitalize first letter
        result = re.sub(r'^\s*([a-z])', lambda m: m.group(1).upper(), result)
        return result

    @staticmethod
    def casual_mode(text: str) -> str:
        replacements = {
            r'\bHowever\b': 'But',
            r'\bTherefore\b': 'So',
            r'\bFurthermore\b': 'Also',
            r'\bAdditionally\b': 'Plus',
            r'\bNevertheless\b': 'Still',
            r'\bConsequently\b': 'So',
            r'\bMoreover\b': 'Also',
            r'\bUtilize\b': 'Use',
            r'\butilize\b': 'use',
            r'\bPurchase\b': 'Buy',
            r'\bpurchase\b': 'buy',
            r'\bObtain\b': 'Get',
            r'\bobtain\b': 'get',
            r'\bCommence\b': 'Start',
            r'\bcommence\b': 'start',
            r'\bTerminate\b': 'End',
            r'\bterminate\b': 'end',
            r'\bPrior to\b': 'Before',
            r'\bSubsequent to\b': 'After',
            r'\bIn order to\b': 'To',
            r'\bDue to the fact that\b': 'Because',
            r'\bAt this point in time\b': 'Now',
            r'\bIn the event that\b': 'If'
        }
        
        result = text
        for old, new in replacements.items():
            result = re.sub(old, new, result)
        return result

    @classmethod
    def normalize(cls, text: str, hedges: bool = True, preambles: bool = True, casual: bool = False) -> str:
        result = text
        if preambles:
            result = cls.remove_preambles(result)
        if hedges:
            result = cls.reduce_hedges(result)
        if casual:
            result = cls.casual_mode(result)
        return result
