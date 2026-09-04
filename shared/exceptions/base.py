from typing import Any


class LeadforixError(Exception):
    """Base exception for all Leadforix domain and infrastructure errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class DatabaseError(LeadforixError):
    """Base database failure exception."""

    def __init__(
        self,
        message: str = "A database error occurred",
        code: str = "DATABASE_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, status_code=status_code, details=details)


class DatabaseConnectionError(DatabaseError):
    """Raised when the service cannot establish or maintain a connection to PostgreSQL."""

    def __init__(
        self,
        message: str = "Unable to connect to database service",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="DATABASE_CONNECTION_ERROR",
            status_code=503,
            details=details,
        )


class EntityNotFoundError(LeadforixError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        entity_name: str,
        entity_id: Any,
    ) -> None:
        super().__init__(
            message=f"{entity_name} with id '{entity_id}' was not found",
            code="ENTITY_NOT_FOUND",
            status_code=404,
            details={"entity_name": entity_name, "entity_id": str(entity_id)},
        )


class DuplicateEntityError(LeadforixError):
    """Raised on unique constraint or idempotency collision."""

    def __init__(
        self,
        entity_name: str,
        field: str,
        value: Any,
    ) -> None:
        super().__init__(
            message=f"{entity_name} with {field}='{value}' already exists",
            code="DUPLICATE_ENTITY",
            status_code=409,
            details={"entity_name": entity_name, "field": field, "value": str(value)},
        )
