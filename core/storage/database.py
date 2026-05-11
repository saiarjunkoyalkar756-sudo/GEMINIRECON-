from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL
from core.storage.models import Base

engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    connect_args={"server_settings": {"jit": "off"}},
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# For asyncpg compatibility with PgBouncer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
import sqlalchemy.dialects.postgresql.asyncpg as asyncpg_dialect

# Disable statement cache for asyncpg to be compatible with transaction-mode pgbouncer
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"statement_cache_size": 0}
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
