from shared.exceptions.base import (
    DatabaseConnectionError,
    DatabaseError,
    DuplicateEntityError,
    EntityNotFoundError,
    LeadforixError,
)
from shared.exceptions.handlers import (
    ErrorDetail,
    ErrorResponse,
    register_exception_handlers,
)

__all__ = [
    "LeadforixError",
    "DatabaseError",
    "DatabaseConnectionError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "ErrorDetail",
    "ErrorResponse",
    "register_exception_handlers",
]
