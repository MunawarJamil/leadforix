import os

# other imports
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
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

# CORS Middleware configuration for frontend SPA integration
cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:80,http://127.0.0.1:3000,http://127.0.0.1:5173",
)
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register common error handlers for uniform API error responses
register_exception_handlers(app)

# Mount routes:
# 1. Root-level for Traefik API Gateway (since Traefik strips the '/api/auth' prefix)
# 2. Direct standalone calls
app.include_router(auth_router)


@app.get("/")
async def root():
    """
    Root service greeting endpoint.
    Returns a basic greeting message identifying the service.
    """
    return {"message": "Welcome to the leadforix auth service"}


@app.get("/health/live", summary="Process Liveness Probe")
async def liveness_check():
    """
    Liveness probe verifying that the FastAPI worker process is responsive.
    Does NOT probe backing stores (PostgreSQL/Redis) to prevent orchestrator
    restart loops during transient network blips.
    """
    return {"status": "live", "service": SERVICE_NAME}


@app.get("/health/ready", summary="Dependency Readiness Probe")
async def readiness_check():
    """
    Readiness probe verifying that the microservice and its backing dependencies
    (PostgreSQL) are operational and ready to accept ingress traffic.
    """
    db_healthy = await ping_database()
    response_payload = {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "status": "ready" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
    }
    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=response_payload)


@app.get("/health", summary="Consolidated Health Probe (Backward Compatible)")
async def health_check():
    """
    Legacy / consolidated health endpoint maintaining backward compatibility with status="ok".
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
