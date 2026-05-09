from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.storage.database import get_db
from core.storage.models import Vulnerability
from sqlalchemy import select
from typing import List

router = APIRouter()

@router.get("/")
async def list_vulnerabilities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vulnerability))
    vulns = result.scalars().all()
    return vulns

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    # Basic severity count (simplified)
    result = await db.execute(select(Vulnerability))
    vulns = result.scalars().all()
    stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for v in vulns:
        stats[v.severity.value] += 1
    return stats
