from fastapi import FastAPI

app = FastAPI(title="Leadforix campaign service")


@app.get("/")
def root():
    return {"message": "Welcome to the leadforix campaign service"}


@app.get("/health")
def health_check():
    return {"service": "campaign_service", "version": "1.0.0", "status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8003)
