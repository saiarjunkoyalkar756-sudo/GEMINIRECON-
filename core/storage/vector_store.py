import os
import logging
from typing import List, Dict, Any, Optional
from upstash_vector import Index
from core.config import UPSTASH_VECTOR_REST_URL, UPSTASH_VECTOR_REST_TOKEN

logger = logging.getLogger(__name__)

class VectorMemory:
    def __init__(self):
        self.enabled = False
        if UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN:
            try:
                self.index = Index(url=UPSTASH_VECTOR_REST_URL, token=UPSTASH_VECTOR_REST_TOKEN)
                self.enabled = True
                logger.info("Upstash Vector storage initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Upstash Vector index: {e}")

    def store_finding(self, finding_id: str, content: str, metadata: Dict[str, Any]):
        if not self.enabled:
            return
        
        try:
            self.index.upsert(
                vectors=[
                    (finding_id, content, metadata)
                ]
            )
        except Exception as e:
            logger.error(f"Failed to store finding in vector memory: {e}")

    def query_memory(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        
        try:
            results = self.index.query(
                data=query_text,
                top_k=top_k,
                include_metadata=True,
                include_data=True
            )
            return [
                {
                    "id": r.id,
                    "content": r.data,
                    "metadata": r.metadata,
                    "score": r.score
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Failed to query vector memory: {e}")
            return []

# Global vector memory instance
vector_memory = VectorMemory()
