from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.system.health import router as system_router
from app.common.exceptions import register_exception_handlers
from app.common.logger import configure_logging, get_logger
from app.config import settings
from app.database.connection import engine
from app.middleware.request_id import RequestIDMiddleware


configure_logging()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting {} v{}",
        settings.APP_NAME,
        settings.APP_VERSION,
    )

    yield

    if engine:
        await engine.dispose()

    logger.info("Application stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(RequestIDMiddleware)


register_exception_handlers(app)


app.include_router(
    system_router,
    prefix=f"{settings.API_V1_PREFIX}/system",
)


app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
async def root() -> dict:
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }