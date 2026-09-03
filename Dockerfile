FROM python:3.14-slim

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install dependencies first for Docker layer caching
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY apps ./apps
COPY shared ./shared
COPY infrastructure ./infrastructure

# Default command (overridden per service in docker-compose)
CMD ["uvicorn", "apps.services.auth_service.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
