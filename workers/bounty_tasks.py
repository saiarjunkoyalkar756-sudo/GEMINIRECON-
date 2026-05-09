import asyncio
from core.storage.database import AsyncSessionLocal
from core.storage.models import ScanJob, JobStatus, ScanLog, Finding
from modules.offensive.sqli_scanner import SQLiScanner
from modules.offensive.xss_scanner import XSSScanner
from modules.offensive.fuzzer import FFufScanner
from scanners.subfinder import SubfinderScanner
from scanners.nmap import NmapScanner
from scanners.nuclei import NucleiScanner
from sqlalchemy import update
from datetime import datetime
import json

async def log_to_db(db, scan_job_id, level, message):
    new_log = ScanLog(scan_job_id=scan_job_id, level=level, message=message)
    db.add(new_log)
    await db.commit()
    print(f"[{level}] {message}")

async def run_bounty_workflow(scan_job_id, target_url, workflow_type="full_recon"):
    async with AsyncSessionLocal() as db:
        await db.execute(update(ScanJob).where(ScanJob.id == scan_job_id).values(status=JobStatus.RUNNING, start_time=datetime.utcnow()))
        await db.commit()

        try:
            await log_to_db(db, scan_job_id, "INFO", f"🚀 Starting Advanced Bounty Workflow: {workflow_type}")
            
            # Chainable Engine
            if workflow_type == "full_recon":
                # Step 1: Recon
                await log_to_db(db, scan_job_id, "INFO", "🔍 Recon Stage...")
                await SubfinderScanner(target_url, scan_job_id).run()
                await NmapScanner(target_url, scan_job_id).run()
                
                # Step 2: Intelligent Fuzzing
                await log_to_db(db, scan_job_id, "INFO", "🗄️  Directory Fuzzing...")
                await FFufScanner(target_url, scan_job_id).run()
                
                # Step 3: Exploitation Probing
                await log_to_db(db, scan_job_id, "INFO", "🛡️  Nuclei/XSS/SQLi Chain...")
                await NucleiScanner(target_url, scan_job_id).run()
                await XSSScanner(target_url, scan_job_id).run()
                await SQLiScanner(target_url, scan_job_id).run()

            await db.execute(update(ScanJob).where(ScanJob.id == scan_job_id).values(status=JobStatus.COMPLETED, end_time=datetime.utcnow()))
            await db.commit()
            await log_to_db(db, scan_job_id, "INFO", "✅ Advanced Bounty Pipeline complete.")

        except Exception as e:
            await log_to_db(db, scan_job_id, "ERROR", f"❌ Pipeline failed: {str(e)}")
            await db.execute(update(ScanJob).where(ScanJob.id == scan_job_id).values(status=JobStatus.FAILED))
            await db.commit()
