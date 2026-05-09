from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.storage.database import get_db
from core.storage.models import User
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

router = APIRouter()

class UserSchema(BaseModel):
    username: str
    email: str

@router.get("/", response_model=List[dict])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]
