from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.storage.database import get_db, AsyncSessionLocal
from core.storage.models import ScanJob, Target, JobStatus, ScanLog
from workers.bounty_tasks import run_bounty_workflow
from reports.generator import ReportGenerator
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, AI_MODEL
import asyncio
import json

router = APIRouter()

class ScanCreate(BaseModel):
    target_url: str
    workflow_type: str = "full_recon"
    options: dict = {}

@router.post("/")
async def create_scan(data: ScanCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
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
    
    scan_job = ScanJob(target_id=target.id, status=JobStatus.PENDING, options=data.options)
    db.add(scan_job)
    await db.commit()
    await db.refresh(scan_job)
    
    background_tasks.add_task(run_bounty_workflow, scan_job.id, url, data.workflow_type)
    
    return {"scan_id": scan_job.id, "status": "queued", "workflow": data.workflow_type}

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
            "results_summary": s.results_summary
        }
        for s in scans
    ]

@router.get("/{scan_id}/report")
async def download_report(scan_id: int, db: AsyncSession = Depends(get_db)):
    query = select(ScanJob).where(ScanJob.id == scan_id).options(
        selectinload(ScanJob.target),
        selectinload(ScanJob.vulnerabilities)
    )
    result = await db.execute(query)
    scan_job = result.scalars().first()
    
    if not scan_job:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    generator = ReportGenerator(scan_job)
    pdf_path = generator.generate_pdf()
    
    return FileResponse(
        pdf_path, 
        media_type="application/pdf", 
        filename=f"GEMINIRECON_Report_{scan_job.target.domain}_{scan_id}.pdf"
    )

@router.websocket("/ws/logs/{scan_id}")
async def websocket_logs(websocket: WebSocket, scan_id: int):
    await websocket.accept()
    last_log_id = 0
    try:
        while True:
            async with AsyncSessionLocal() as db:
                query = select(ScanLog).where(ScanLog.scan_job_id == scan_id, ScanLog.id > last_log_id).order_by(ScanLog.id)
                result = await db.execute(query)
                logs = result.scalars().all()
                
                for log in logs:
                    await websocket.send_json({
                        "level": log.level,
                        "message": log.message,
                        "timestamp": log.timestamp.isoformat()
                    })
                    last_log_id = log.id
            
            await asyncio.sleep(1) 
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for scan {scan_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
