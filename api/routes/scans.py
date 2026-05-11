from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.storage.database import get_db
from core.storage.models import ScanJob, Target, JobStatus
from workers.tasks import run_scan_task
from pydantic import BaseModel
from sqlalchemy import select
import json

router = APIRouter()

class ScanCreate(BaseModel):
    target_url: str
    workflow_type: str = "subdomain_enumeration"
    options: dict = {}

@router.post("/")
async def create_scan(data: ScanCreate, db: AsyncSession = Depends(get_db)):
    url = data.target_url
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
        
    target_domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    
    result = await db.execute(select(Target).where(Target.domain == target_domain))
    target = result.scalars().first()
    
    if not target:
        target = Target(domain=target_domain)
        db.add(target)
        await db.commit()
        await db.refresh(target)
    
    scan_job = ScanJob(
        target_id=target.id, 
        status=JobStatus.PENDING, 
        options={**data.options, "skill": data.workflow_type}
    )
    db.add(scan_job)
    await db.commit()
    await db.refresh(scan_job)
    
    # Trigger Celery task
    run_scan_task.delay(scan_job.id, url)
    
    return {"scan_id": scan_job.id, "status": "queued", "skill": data.workflow_type}

@router.get("/")
async def list_scans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScanJob).order_by(ScanJob.id.desc()))
    scans = result.scalars().all()
    return [
        {
            "id": s.id,
            "target_id": s.target_id,
            "status": s.status.value,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "results_summary": s.results_summary,
            "skill": s.options.get("skill") if s.options else "unknown"
        }
        for s in scans
    ]

@router.get("/{scan_id}/report")
async def download_report(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScanJob).where(ScanJob.id == scan_id))
    scan_job = result.scalars().first()
    
    if not scan_job or not scan_job.results_summary:
        raise HTTPException(status_code=404, detail="Report not ready or scan not found")
    
    # In the new architecture, the report path might be in the summary or we can regenerate it
    try:
        summary = json.loads(scan_job.results_summary)
        pdf_path = summary.get("pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            return FileResponse(pdf_path, media_type="application/pdf")
    except:
        pass
    
    raise HTTPException(status_code=404, detail="PDF report not found on disk")
