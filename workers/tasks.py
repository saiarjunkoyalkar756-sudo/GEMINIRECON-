import asyncio
from celery import Celery
from core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from core.storage.database import AsyncSessionLocal
from core.storage.models import ScanJob, JobStatus, Vulnerability, Target, Asset, Finding
from tools.registry import registry
from execution.engine import execution_engine
from agents.orchestrator import ReconOrchestrator
from sqlalchemy import update
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

import ssl

celery_app = Celery(
    "tasks", 
    broker=CELERY_BROKER_URL, 
    backend=CELERY_RESULT_BACKEND,
    broker_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE},
    redis_backend_use_ssl={'ssl_cert_reqs': ssl.CERT_NONE}
)

from core.events import event_bus

async def log_to_db(db, scan_job_id, level, message):
    from core.storage.models import ScanLog
    new_log = ScanLog(scan_job_id=scan_job_id, level=level, message=message)
    db.add(new_log)
    await db.commit()
    logger.info(f"[{level}] {message}")
    # Publish to event bus for real-time UI updates
    await event_bus.publish_log(scan_job_id, level, message)

@celery_app.task(name="run_scan")
def run_scan_task(scan_job_id: int, target_url: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_recon_pipeline(scan_job_id, target_url))

async def run_recon_pipeline(scan_job_id: int, target_url: str):
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(ScanJob)
            .where(ScanJob.id == scan_job_id)
            .values(status=JobStatus.RUNNING, start_time=datetime.utcnow())
        )
        await db.commit()
        
        orchestrator = ReconOrchestrator()
        
        async def progress_callback(msg):
            await log_to_db(db, scan_job_id, "INFO", msg)
            # Here we could also push to a WebSocket
            
        try:
            results = await orchestrator.run_recon_workflow(target_url, callback=progress_callback)
            
            # Save results to DB
            await db.execute(
                update(ScanJob)
                .where(ScanJob.id == scan_job_id)
                .values(
                    status=JobStatus.COMPLETED, 
                    end_time=datetime.utcnow(),
                    results_summary=json.dumps(results)
                )
            )
            await db.commit()
            
        except Exception as e:
            await log_to_db(db, scan_job_id, "ERROR", f"Pipeline failed: {str(e)}")
            await db.execute(
                update(ScanJob)
                .where(ScanJob.id == scan_job_id)
                .values(status=JobStatus.FAILED)
            )
            await db.commit()
