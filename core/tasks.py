from celery import Celery
import os
from core.config import REDIS_URL

celery = Celery("geminirecon", broker=REDIS_URL, backend=REDIS_URL)

@celery.task(name="recon_task")
def recon_task(target):
    # This is where your pipeline logic will be triggered by Celery
    import subprocess
    print(f"[*] Celery: Starting recon on {target}")
    return {"status": "completed", "target": target}
