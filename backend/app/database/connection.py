from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings

# Use psycopg async driver for Supabase pgbouncer (avoids asyncpg prepared statement issues)
if settings.DATABASE_URL and "pooler" in settings.DATABASE_URL:
    # Convert asyncpg URL to psycopg async URL
    psycopg_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    engine: AsyncEngine = create_async_engine(
        psycopg_url,
        echo=settings.DEBUG,
        poolclass=pool.NullPool,
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