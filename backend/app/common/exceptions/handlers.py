from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from app.common.logger import get_logger


logger = get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> ORJSONResponse:
        request_id = getattr(request.state, "request_id", None)

        logger.exception(
            "Unhandled exception | request_id={} | path={}",
            request_id,
            request.url.path,
        )

        return ORJSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                    "request_id": request_id,
                }
            },
        )