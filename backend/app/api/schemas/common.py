from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: dict = Field(
        ...,
        example={
            "code": "VALIDATION_ERROR",
            "message": "Invalid input",
            "details": {},
        },
    )


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: dict | None = None


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
