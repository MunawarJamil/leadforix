"""
Lead Service main application bootstrap.

Design Patterns:
- Application Factory / Bootstrap Pattern: Initializes FastAPI with routes, middleware,
  exception handlers, and lifecycle hooks.
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.services.lead_service.app.api.routes import router as discovery_router
from shared.database import ping_database
from shared.exceptions import register_exception_handlers
from shared.logging import get_logger, setup_logging

SERVICE_NAME = "lead_service"

# Initialize structured JSON logging
setup_logging(service_name=SERVICE_NAME)
logger = get_logger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycles."""
    logger.info("Starting up %s...", SERVICE_NAME)
    is_db_ready = await ping_database()
    logger.info("Database connectivity check on startup: %s", "reachable" if is_db_ready else "unreachable")
    yield
    logger.info("Shutting down %s...", SERVICE_NAME)


root_path = os.getenv("ROOT_PATH", "/api/lead")
app = FastAPI(
    title="Leadforix Lead Service",
    lifespan=lifespan,
    root_path=root_path,
)

# CORS Middleware configuration
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

# Standard error response handlers
register_exception_handlers(app)

# Mount domain routers
app.include_router(discovery_router)


@app.get("/")
def root():
    return {"message": "Welcome to the leadforix lead service"}


@app.get("/health/live", summary="Process Liveness Probe")
async def liveness_check():
    return {"status": "live", "service": SERVICE_NAME}


@app.get("/health/ready", summary="Dependency Readiness Probe")
async def readiness_check():
    db_healthy = await ping_database()
    response_payload = {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "status": "ready" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
    }
    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=response_payload)


@app.get("/health", summary="Consolidated Health Probe")
async def health_check():
    return {"service": SERVICE_NAME, "version": "1.0.0", "status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=True)
