from sqlalchemy import event, pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings

# Disable prepared statements and connection pooling for Supabase pgbouncer pooler
if settings.DATABASE_URL and "pooler" in settings.DATABASE_URL:
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        poolclass=pool.NullPool,
    ) if settings.DATABASE_URL and settings.DATABASE_URL.strip() else None

    # Disable prepared statements for pgbouncer
    if engine is not None:
        @event.listens_for(engine.sync_engine, "connect")
        def set_statement_cache_size(dbapi_connection, connection_record):
            dbapi_connection.statement_cache_size = 0
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