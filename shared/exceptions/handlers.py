import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import DBAPIError, OperationalError, SQLAlchemyError

from shared.exceptions.base import DatabaseConnectionError, LeadforixError

logger = logging.getLogger("leadforix.api")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


def register_exception_handlers(app: FastAPI) -> None:
    """Register uniform error handlers across all FastAPI microservices."""

    @app.exception_handler(LeadforixError)
    async def leadforix_exception_handler(_: Request, exc: LeadforixError) -> JSONResponse:
        logger.warning("Handled business error [%s]: %s", exc.code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                )
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="VALIDATION_ERROR",
                    message="Invalid request payload or parameters",
                    details={"errors": exc.errors()},
                )
            ).model_dump(),
        )

    @app.exception_handler(OperationalError)
    @app.exception_handler(DBAPIError)
    async def db_connection_error_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error("Database connection failure: %s", str(exc), exc_info=True)
        # Avoid leaking internal connection strings or DB traces to external clients
        conn_err = DatabaseConnectionError()
        return JSONResponse(
            status_code=conn_err.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=conn_err.code,
                    message=conn_err.message,
                )
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server exception: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="An unexpected internal server error occurred",
                )
            ).model_dump(),
        )
