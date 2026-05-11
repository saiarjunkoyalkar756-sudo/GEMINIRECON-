import redis.asyncio as redis
from core.config import REDIS_URL
import json
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)

    async def publish_log(self, scan_job_id: int, level: str, message: str):
        event = {
            "type": "log",
            "scan_job_id": scan_job_id,
            "level": level,
            "message": message
        }
        try:
            await self.redis.publish(f"scan:{scan_job_id}", json.dumps(event))
        except Exception as e:
            logger.warning(f"Could not publish to Redis: {e}")

    async def subscribe_to_scan(self, scan_job_id: int):
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(f"scan:{scan_job_id}")
            return pubsub
        except Exception as e:
            logger.error(f"Could not subscribe to Redis: {e}")
            return None

event_bus = EventBus()
