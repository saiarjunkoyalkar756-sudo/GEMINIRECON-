import asyncio
import json
import os
from core.storage.database import init_db, AsyncSessionLocal
from core.storage.models import ScanJob, Target, JobStatus
from workers.tasks import run_full_recon_pipeline
from sqlalchemy import select

async def manual_test(target_url):
    print(f"[*] Starting Manual Test for {target_url}")
    
    # Initialize DB
    await init_db()
    
    target_domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]
    
    async with AsyncSessionLocal() as db:
        # Check if target exists
        result = await db.execute(select(Target).where(Target.domain == target_domain))
        target = result.scalars().first()
        
        if not target:
            target = Target(domain=target_domain)
            db.add(target)
            await db.commit()
            await db.refresh(target)
        
        # Create Scan Job
        scan_job = ScanJob(target_id=target.id, status=JobStatus.PENDING, options={"full_recon": True})
        db.add(scan_job)
        await db.commit()
        await db.refresh(scan_job)
        
        scan_id = scan_job.id
        print(f"[+] Created Scan Job ID: {scan_id}")

    # Run Pipeline directly
    try:
        await run_full_recon_pipeline(scan_id, target_url)
        print(f"[+] Pipeline completed for {target_url}")
        
        # Fetch results
        async with AsyncSessionLocal() as db:
            # Refresh job from DB
            result = await db.execute(select(ScanJob).where(ScanJob.id == scan_id))
            job = result.scalars().first()
            
            print("\n" + "="*50)
            print(f"RESULTS FOR {target_url}")
            print("="*50)
            print(f"Status: {job.status.value}")
            if job.results_summary:
                print(f"\n[AI SUMMARY]\n{job.results_summary}")
            else:
                print("\n[!] No AI summary generated (likely due to missing API keys or errors).")
                
    except Exception as e:
        print(f"[!] Test failed: {e}")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "http://kitss.edu.in"
    asyncio.run(manual_test(target))
