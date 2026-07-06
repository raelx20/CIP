from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings


engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)