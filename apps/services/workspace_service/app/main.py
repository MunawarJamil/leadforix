from fastapi import FastAPI


import asyncio

from contextlib import asynccontextmanager
from apps.services.workspace_service.app.infrastructure.consumer import run_workspace_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background consumer worker for RabbitMQ messages
    consumer_task = asyncio.create_task(run_workspace_consumer())
    yield
    # Shutdown: Clean cancellation
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Leadforix workspace service")

@app.get("/")
def root():
    return {"message": "Welcome to the leadforix workspace service"}


@app.get("/health")
def health_check():
    return {"service": "workspace_service", "version": "1.0.0", "status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8008)
