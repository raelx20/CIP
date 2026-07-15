from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings

_engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
}

# Disable prepared statements for Supabase pgbouncer pooler
if settings.DATABASE_URL and "pooler" in settings.DATABASE_URL:
    _engine_kwargs["poolclass"] = pool.NullPool
    _engine_kwargs["connect_args"] = {"statement_cache_size": 0}

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **_engine_kwargs,
) if settings.DATABASE_URL and settings.DATABASE_URL.strip() else None