import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.exceptions import (
    DatabaseConnectionError,
    DuplicateEntityError,
    EntityNotFoundError,
    LeadforixError,
    register_exception_handlers,
)


@pytest.fixture
def test_app() -> FastAPI:
    """
    Create a lightweight FastAPI application wired with the shared error handlers.
    Provides isolated endpoints to test exception status codes and response structures.
    """
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/trigger-not-found")
    def trigger_not_found():
        raise EntityNotFoundError(entity_name="Lead", entity_id="lead_123")

    @app.get("/trigger-duplicate")
    def trigger_duplicate():
        raise DuplicateEntityError(entity_name="User", field="email", value="test@example.com")

    @app.get("/trigger-db-connection-error")
    def trigger_db_conn_error():
        raise DatabaseConnectionError()

    @app.get("/trigger-generic-error")
    def trigger_generic():
        raise LeadforixError(message="Custom business failure", code="CUSTOM_CODE", status_code=400)

    return app


def test_entity_not_found_returns_404(test_app: FastAPI):
    """
    Verify that EntityNotFoundError returns HTTP 404 with standardized error payload.
    """
    client = TestClient(test_app)
    response = client.get("/trigger-not-found")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "ENTITY_NOT_FOUND"
    assert "lead_123" in data["error"]["message"]


def test_duplicate_entity_returns_409(test_app: FastAPI):
    """
    Verify that DuplicateEntityError returns HTTP 409 conflict with duplicate field context.
    """
    client = TestClient(test_app)
    response = client.get("/trigger-duplicate")
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DUPLICATE_ENTITY"


def test_db_connection_error_returns_503(test_app: FastAPI):
    """
    Verify that DatabaseConnectionError returns HTTP 503 without leaking internal traces.
    """
    client = TestClient(test_app)
    response = client.get("/trigger-db-connection-error")
    assert response.status_code == 503
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DATABASE_CONNECTION_ERROR"


def test_custom_error_returns_custom_status(test_app: FastAPI):
    """
    Verify that arbitrary LeadforixError subtypes respect their defined status code.
    """
    client = TestClient(test_app)
    response = client.get("/trigger-generic-error")
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CUSTOM_CODE"
