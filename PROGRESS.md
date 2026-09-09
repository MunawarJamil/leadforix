# Leadforix — Development Progress & Session Handover

This file is the single source of truth for **where we left off, what has been completed, and what to do next**.
Any AI model or developer starting a new chat session should read this file first to resume immediately without re-exploring the whole repository.

---

## 1. Current Phase & Ticket

- **Current Ticket**: Day 04 — Auth Service: Authentication
- **Status**: Completed

---

## 2. What Has Been Done So Far

- [x] **Monorepo Structure**: Root `pyproject.toml`, `.python-version`, `.venv`, and `uv` lockfile configured.
- [x] **8 Microservices Scaffolding**:
  - `agent_service` (port 8001, `/api/agent`)
  - `auth_service` (port 8002, `/api/auth`)
  - `campaign_service` (port 8003, `/api/campaign`)
  - `knowledge_service` (port 8004, `/api/knowledge`)
  - `lead_service` (port 8005, `/api/lead`)
  - `outreach_service` (port 8006, `/api/outreach`)
  - `research_service` (port 8007, `/api/research`)
  - `workspace_service` (port 8008, `/api/workspace`)
- [x] **Clean Architecture Directories**: Each service has `app/{api, application, domain, infrastructure}` and `test/`.
- [x] **API Gateway (Traefik v3.5)**:
  - `infrastructure/api_gateway/traefik/traefik.yml` (ports 80 & 8080 dashboard)
  - `infrastructure/api_gateway/traefik/dynamic/routes.yml` configured with internal Docker service routing.
- [x] **Day 02 Stack & Infrastructure**:
  - Unified `Dockerfile` and `.dockerignore` configured with `python:3.14-slim` and `uv`.
  - Celery worker foundation (`infrastructure/messaging/celery_app.py`).
  - Centralized `infrastructure/docker-compose.yml` with PostgreSQL 16, Redis 7, Qdrant, Traefik, and 8 FastAPI microservices.
  - Dedicated bridge network `leadforix-network` with Docker DNS and persistent named volumes.
- [x] **Day 03 Database Foundation & Shared Infrastructure**:
  - Installed `sqlalchemy>=2.0.52`, `asyncpg>=0.31.0`, `alembic>=1.19.1`, `pydantic-settings>=2.15.0`, `pytest-asyncio>=1.4.0`.
  - Shared database config with automatic dialect normalization (`postgresql+asyncpg://`) and connection pool tuning (`shared/config/database.py`).
  - Declarative Base with `AsyncAttrs`, `UUIDPrimaryKeyMixin`, and `TimestampMixin` (`shared/database/base.py`).
  - Async engine, session factory, transaction context manager, and ping utility (`shared/database/session.py`).
  - Async migrations foundation with Alembic (`alembic.ini`, `infrastructure/database/alembic/`).
  - Common domain/DB exception hierarchy and standard FastAPI JSON error handlers (`shared/exceptions/`).
  - Structured JSON logging foundation emitting to stdout (`shared/logging/logger.py`).
  - Live PostgreSQL connectivity check and structured logging wired into `auth_service` (`apps/services/auth_service/app/main.py`).
- [x] **Day 04 Auth Service — Authentication**:
  - Cryptographic dependencies installed: `pyjwt>=2.8.0`, `bcrypt>=4.0.0`.
  - Security configuration with environment variables (`AuthSettings` in `apps/services/auth_service/app/infrastructure/config.py`).
  - Domain models: `UserRole` (`OWNER`, `ADMIN`, `SALES_USER`, `AGENT`) and pure immutable entities `User`, `RefreshToken` (`apps/services/auth_service/app/domain/`).
  - Persistence Layer: `UserModel` & `RefreshTokenModel` ORM mapping, indexed SHA-256 token hashes, and Alembic revision `001_create_auth_tables`.
  - Security Layer: `PasswordHasher` with adaptive bcrypt salting & constant-time check; `TokenService` for signed JWT access tokens and opaque refresh tokens.
  - Application Layer: `AuthRepository` and `AuthService` handling registration, authentication, single-use token rotation, and logout revocation.
  - API Layer: Request/Response DTO schemas, `POST /register`, `POST /login`, `POST /refresh`, `POST /logout`, protected `GET /me`.
  - Security Dependencies: `get_current_user` JWT bearer guard and higher-order `require_roles` RBAC policy dependency.
  - Shared domain exceptions added: `AuthenticationError` (401), `AuthorizationError` (403), `ConflictError` (409).
  - 28/28 unit tests passing across all suites (`tests/unit/test_auth.py`, `test_database.py`, `test_exceptions.py`, `test_health.py`).

---

## 3. Key Decisions & Architectural Rules

1. **`main.py` Location**: Entry point belongs at `<service>/app/main.py` per Clean Architecture.
2. **AsyncIO Native**: All database interactions use SQLAlchemy 2.0 async engine and `asyncpg`. Standard `postgresql://` URLs in `.env` are automatically normalized.
3. **Connection Pooling**: Pre-ping is enabled by default to drop dead sockets cleanly.
4. **Service Isolation**: No cross-service database access. Models and services inherit from shared base abstractions without referencing another service's tables.
5. **Standardized Errors (Rule 17)**: DB connection failures return `503 DATABASE_CONNECTION_ERROR`; auth failures return `401 AUTHENTICATION_ERROR`; conflicts return `409 CONFLICT` without leaking internal traces.
6. **Structured Logging**: Services emit JSON logs to `sys.stdout` for container observability.
7. **Token Rotation & Defense in Depth**: Refresh tokens are stored strictly as SHA-256 digests in the DB; refreshing immediately invalidates the old token and issues a new pair.
8. **Host Database Port (5433)**: Docker Postgres is mapped to host port `5433:5432` to avoid collision with any local native PostgreSQL installations (such as Postgres 18 on Windows).
9. **Docker Compose Profiles & Selective Running**: Services inherit `profiles: ["full"]`. Core infra (`postgres`, `redis`, `traefik`) runs by default; individual services can be started on-demand (`docker compose up -d traefik <service>`), or everything with `--profile full`.

---

## 4. Current Status — Day 04 Done

**Day 04 Acceptance Criteria Achieved:**
- Passwords are never stored in plaintext (salted bcrypt one-way hashing).
- Access tokens authenticate protected endpoints (`/me` with Bearer token).
- Refresh tokens issue new access tokens with single-use token rotation.
- Invalid/expired tokens are rejected cleanly with 401.
- Logout invalidates the refresh-token flow in the database.
- Unit test suite covers cryptographic primitives, domain models, and API endpoints (28/28 passing).

---

## 5. Immediate Next Steps (Day 05 Preview)

Ready for **DAY-05** requirements.

---

## 6. Session Handover Instructions for New Chats

When the user starts a new chat and says:
> *"Let's continue where we left off"* or *"What's next?"*

The agent must:
1. Read this file ([PROGRESS.md](file:///e:/PERSONAL-PROJECTS/leadforix/PROGRESS.md)) and [AGENTS.md](file:///e:/PERSONAL-PROJECTS/leadforix/AGENTS.md).
2. Check section **4. Immediate Next Steps** above.
3. State the immediate task to the user and proceed with that single step. Do not re-explore the repository from scratch.
4. Follow the step-by-step workflow:
   - **Step 0**: Suggest creating a new branch in chat (`feat/lf-XX-task-name`), do not create it directly.
   - Explain task and flow concisely with a short plan -> propose Step 1 -> wait for approval (`done`).
   - Guide what/where/why (no direct code edits unless explicitly requested).
   - Once verified, provide a meaningful conventional commit message.
5. Synchronize with Mem0 MCP memory upon task completion.


