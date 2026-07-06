from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

from app.config import settings
from app.database.connection import engine


router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready")
async def readiness_check():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "connected",
        }

    except Exception:
        return ORJSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "unavailable",
            },
        )