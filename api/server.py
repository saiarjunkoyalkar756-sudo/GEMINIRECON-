from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.storage.database import get_db
from core.tasks import recon_task
from pydantic import BaseModel

app = FastAPI(title="GEMINIRECON Enterprise API")

class TargetInput(BaseModel):
    target: str

@app.post("/api/scan")
async def trigger_scan(data: TargetInput):
    task = recon_task.delay(data.target)
    return {"task_id": task.id, "status": "queued"}

@app.get("/api/vulnerabilities")
async def list_findings(db: AsyncSession = Depends(get_db)):
    # Query implementation using the SQLAlchemy model
    return {"status": "success", "data": []}
