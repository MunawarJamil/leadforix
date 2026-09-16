import asyncio
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from apps.services.workspace_service.app.api.routes import router as workspace_router
from apps.services.workspace_service.app.infrastructure.consumer import run_workspace_consumer
from shared.database import ping_database
from shared.exceptions import register_exception_handlers
from shared.logging import get_logger, setup_logging

SERVICE_NAME = "workspace_service"

setup_logging(service_name=SERVICE_NAME)
logger = get_logger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Background consumer worker start karein
    logger.info("Starting up %s...", SERVICE_NAME)
    is_db_ready = await ping_database()
    logger.info("Database connectivity check: %s", "reachable" if is_db_ready else "unreachable")
    
    consumer_task = asyncio.create_task(run_workspace_consumer())
    yield
    # Shutdown: Clean cancellation
    logger.info("Shutting down %s consumer...", SERVICE_NAME)
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


root_path = os.getenv("ROOT_PATH", "/api/workspace")
app = FastAPI(
    title="Leadforix Workspace Service",
    lifespan=lifespan,
    root_path=root_path,
)

# Shared Exception Handlers
register_exception_handlers(app)

# Include API Router
app.include_router(workspace_router)


@app.get("/")
def root():
    return {"message": "Welcome to the leadforix workspace service"}


@app.get("/health")
def health_check():
    return {"service": SERVICE_NAME, "version": "1.0.0", "status": "ok"}


@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_probe():
    is_db_up = await ping_database()
    if is_db_up:
        return {"status": "ready", "database": "connected"}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "not_ready", "database": "disconnected"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8008)
