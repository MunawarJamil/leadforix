import os

# other imports
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from apps.services.auth_service.app.api.routes import router as auth_router
from shared.database import ping_database
from shared.exceptions import register_exception_handlers
from shared.logging import get_logger, setup_logging

SERVICE_NAME = "auth_service"

# Initialize structured JSON logging for this service
setup_logging(service_name=SERVICE_NAME)
logger = get_logger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown lifecycles.
    Logs lifecycle events and checks database readiness on boot.
    """
    logger.info("Starting up %s...", SERVICE_NAME)
    is_db_ready = await ping_database()
    db_status = "reachable" if is_db_ready else "unreachable"
    logger.info("Database connectivity check on startup: %s", db_status)
    yield
    logger.info("Shutting down %s...", SERVICE_NAME)


# app = FastAPI(title="Leadforix Auth Service", lifespan=lifespan)

root_path = os.getenv("ROOT_PATH", "/api/auth")
app = FastAPI(
    title="Leadforix Auth Service",
    lifespan=lifespan,
    root_path=root_path,
)

# Register common error handlers for uniform API error responses
register_exception_handlers(app)

# Mount routes:
# 1. Root-level for Traefik API Gateway (since Traefik strips the '/api/auth' prefix)
# 2. Under '/auth' for direct standalone calls (e.g. POST http://localhost:8002/auth/login)
app.include_router(auth_router)

# For now keep it commented
# app.include_router(auth_router, prefix="/auth")


@app.get("/")
async def root():
    """
    Root service greeting endpoint.
    Returns a basic greeting message identifying the service.
    """
    return {"message": "Welcome to the leadforix auth service"}


@app.get("/health")
async def health_check():
    """
    Comprehensive health probe endpoint.
    Verifies service status and live PostgreSQL connectivity, returning 503 if degraded.
    """
    db_healthy = await ping_database()
    response_payload = {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "status": "ok" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
    }
    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=response_payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
