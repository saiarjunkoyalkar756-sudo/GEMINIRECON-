from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.storage.database import get_db
from core.storage.models import Target
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

router = APIRouter()

class TargetSchema(BaseModel):
    domain: str
    organization: str = None

@router.get("/", response_model=List[dict])
async def list_targets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Target))
    targets = result.scalars().all()
    return [{"id": t.id, "domain": t.domain, "organization": t.organization} for t in targets]

@router.post("/")
async def create_target(data: TargetSchema, db: AsyncSession = Depends(get_db)):
    target = Target(domain=data.domain, organization=data.organization)
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target
