import asyncpg
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings

# Disable prepared statements and connection pooling for Supabase pgbouncer pooler
if settings.DATABASE_URL and "pooler" in settings.DATABASE_URL:

    async def get_asyncpg_connection():
        return await asyncpg.connect(settings.DATABASE_URL.replace("+asyncpg", ""), statement_cache_size=0)

    engine: AsyncEngine = create_async_engine(
        "postgresql+asyncpg://",
        echo=settings.DEBUG,
        poolclass=pool.NullPool,
        creator=get_asyncpg_connection,
    ) if settings.DATABASE_URL and settings.DATABASE_URL.strip() else None
else:
    _engine_kwargs = {
        "echo": settings.DEBUG,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    }
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        **_engine_kwargs,
    ) if settings.DATABASE_URL and settings.DATABASE_URL.strip() else None