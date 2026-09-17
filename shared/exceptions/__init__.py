from shared.exceptions.base import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseConnectionError,
    DatabaseError,
    DuplicateEntityError,
    EntityNotFoundError,
    LeadforixError,
    NotFoundError
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
    "NotFoundError",
    "DuplicateEntityError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "ErrorDetail",
    "ErrorResponse",
    "register_exception_handlers",
]
