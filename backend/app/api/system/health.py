from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

from app.config import settings
from app.database.connection import engine

_start_time = datetime.now(timezone.utc)

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": (datetime.now(timezone.utc) - _start_time).total_seconds(),
    }


@router.get("/ready")
async def readiness_check():
    db_status = "unavailable"
    redis_status = "unavailable"

    # Check database
    if engine is not None:
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {type(e).__name__}: {str(e)[:200]}"

    # Check Redis
    try:
        import redis.asyncio as aioredis
        redis_url = getattr(settings, "REDIS_URL", None) or "redis://localhost:6379/0"
        async with aioredis.from_url(redis_url, socket_connect_timeout=2) as client:
            await client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "unavailable"

    is_ready = db_status == "connected"
    status_code = 200 if is_ready else 503

    return ORJSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "database": db_status,
            "redis": redis_status,
        },
    )