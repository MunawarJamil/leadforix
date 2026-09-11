# Leadforix — Development Progress & Session Handover

This file is the single source of truth for **where we left off, what has been completed, and what to do next**.
Any AI model or developer starting a new chat session should read this file first to resume immediately without re-exploring the whole repository.

---

## 1. Current Phase & Ticket

- **Current Phase**: Discovery Pipeline Phase (lead_service)
- **Current Ticket**: TICKET-01 — Build resilient API clients for HN Algolia & Remotive
- **Status**: In Progress

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
  - Async migrations foundation with Alembic (`alembic.ini`, `infrastructure/database/migrations/`).
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
- [x] **Day 05 Auth Service — Authorization & Security Hardening**:
  - **Shared Security Module (`shared/security/`)**: Reusable by all downstream microservices (`workspace_service`, `lead_service`, etc.) to statelessly authenticate requests without DB access. Includes `UserPrincipal`, `SecuritySettings`, `StatelessTokenValidator`, `get_current_user`, `require_roles`, and `require_workspace`.
  - **Downstream Token Claims**: Access tokens enriched with `sub`, `email`, `role`, `workspace_id`, `type="access"`, `iss="leadforix-auth"`, `aud="leadforix-api"`.
  - **Input Sanitization & Password Complexity**: Pydantic validators enforcing whitespace trimming, lowercase emails, and password entropy (min 8 chars, uppercase, lowercase, digit, special character).
  - **RFC 6819 Token Family Reuse Detection**: Re-submitting a revoked refresh token automatically triggers breach invalidation, terminating all active sessions for that user across all devices.
  - **Account Lifecycle States (`UserStatus`)**: Explicit `ACTIVE`, `SUSPENDED`, `PENDING_VERIFICATION` statuses blocking suspended or unverified accounts during login and token refresh.
  - **Password Reset Foundation**: `PasswordResetToken` entity and model storing 64-char CSPRNG SHA-256 digests with 15-minute expiration; `POST /password-reset/request` (anti-enumeration) and `POST /password-reset/confirm` (session termination on password change).
  - **Alembic Migration 002**: `002_add_user_status_and_password_reset.py` adding `status` to `users` and creating `password_reset_tokens` table.
  - **Documentation**: Comprehensive `docs/architecture/service-authentication.md` guide for downstream microservices.
  - **Unit Test Suite**: 38/38 unit tests passing across all suites (`test_security_hardening.py`, `test_auth.py`, `test_database.py`, `test_exceptions.py`, `test_health.py`).
- [x] **Production Hardening & Architectural Refactoring**:
  - **Transaction Persistence Lifecycle**: Added automatic `commit()` on HTTP success and `rollback()` on error in `get_db_session` ([session.py](file:///e:/PERSONAL-PROJECTS/leadforix/shared/database/session.py)).
  - **Service Boundary Decoupling**: Extracted canonical `UserRole` into [shared/security/roles.py](file:///e:/PERSONAL-PROJECTS/leadforix/shared/security/roles.py), removing tight coupling from `auth_service`.
  - **Strict Role Validation**: Enforced enum coercion and validation in `StatelessTokenValidator` ([validator.py](file:///e:/PERSONAL-PROJECTS/leadforix/shared/security/validator.py)).
  - **Connection Pool Tuning**: Sized pool defaults to `pool_size=5, max_overflow=5` in [database.py](file:///e:/PERSONAL-PROJECTS/leadforix/shared/config/database.py) to prevent PostgreSQL starvation across microservices.
  - **Eliminated ORM Query Amplification**: Replaced `lazy="selectin"` with `lazy="raise"` on `UserModel.refresh_tokens` and `reset_tokens` ([models.py](file:///e:/PERSONAL-PROJECTS/leadforix/apps/services/auth_service/app/infrastructure/models.py)), removing 2 redundant SQL queries per user fetch.
  - **Composite Index Optimization**: Added `(user_id, is_revoked)` composite index on `RefreshTokenModel` and created Alembic revision `003_add_composite_index_on_refresh_tokens.py`.
  - **Non-Blocking Bcrypt Concurrency**: Offloaded CPU-bound `bcrypt.hashpw` and `bcrypt.checkpw` to worker thread pool via `asyncio.to_thread` in [security.py](file:///e:/PERSONAL-PROJECTS/leadforix/apps/services/auth_service/app/infrastructure/security.py), preventing async event loop freezes.
  - **Async Service Calls**: Updated `register_user`, `authenticate_user`, and `confirm_password_reset` to `await` password hashing operations in [service.py](file:///e:/PERSONAL-PROJECTS/leadforix/apps/services/auth_service/app/application/service.py).
  - **Atomic Multi-Step Transactions**: Wrapped `confirm_password_reset` in explicit `async with transaction(...)` context in [service.py](file:///e:/PERSONAL-PROJECTS/leadforix/apps/services/auth_service/app/application/service.py).
  - **Frontend CORS Integration**: Attached `CORSMiddleware` with configurable `CORS_ORIGINS` in [main.py](file:///e:/PERSONAL-PROJECTS/leadforix/apps/services/auth_service/app/main.py).
  - **Decoupled SRE Health Probes**: Added non-blocking `/health/live` liveness probe and dependency `/health/ready` readiness probe in [main.py](file:///e:/PERSONAL-PROJECTS/leadforix/apps/services/auth_service/app/main.py).
  - **Container Security Hardening**: Added unprivileged `appuser:appgroup` (UID/GID 10001) in [Dockerfile](file:///e:/PERSONAL-PROJECTS/leadforix/Dockerfile) per CIS Docker benchmarks.
  - **Test Suite Expansion**: Added unit tests in `test_database.py` and `test_health.py`, expanding test coverage to **43/43 passing tests (100%)**.

---

## 3. Key Decisions & Architectural Rules

1. **`main.py` Location**: Entry point belongs at `<service>/app/main.py` per Clean Architecture.
2. **AsyncIO Native**: All database interactions use SQLAlchemy 2.0 async engine and `asyncpg`. Standard `postgresql://` URLs in `.env` are automatically normalized.
3. **Connection Pooling**: Pre-ping is enabled by default to drop dead sockets cleanly.
4. **Service Isolation**: No cross-service database access. Models and services inherit from shared base abstractions without referencing another service's tables.
5. **Standardized Errors (Rule 17)**: DB connection failures return `503 DATABASE_CONNECTION_ERROR`; auth failures return `401 AUTHENTICATION_ERROR`; conflicts return `409 CONFLICT` without leaking internal traces.
6. **Structured Logging**: Services emit JSON logs to `sys.stdout` for container observability.
7. **Token Rotation & Defense in Depth**: Refresh tokens are stored strictly as SHA-256 digests in the DB; refreshing immediately invalidates the old token and issues a new pair.
8. **Token Reuse Breach Invalidation (RFC 6819)**: Re-presenting a revoked refresh token triggers immediate session invalidation for all active tokens belonging to that user.
9. **Stateless Inter-Service Authentication**: Downstream services verify JWTs statelessly via `shared.security` without querying `auth_service` database or making network roundtrips.
10. **Host Database Port (5433)**: Docker Postgres is mapped to host port `5433:5432` to avoid collision with any local native PostgreSQL installations.
11. **Docker Compose Profiles & Selective Running**: Services inherit `profiles: ["full"]`. Core infra (`postgres`, `redis`, `traefik`) runs by default; individual services can be started on-demand (`docker compose up -d traefik <service>`), or everything with `--profile full`.

---

## 4. Current Status — Day 05 Done

**Day 05 Acceptance Criteria Achieved:**
- Downstream microservices can statelessly determine caller identity (`UserPrincipal.id`, `email`).
- Downstream microservices can check user roles via `require_roles("OWNER", "ADMIN")`.
- Downstream microservices can determine and enforce workspace context via `require_workspace` (claim or `X-Workspace-ID` header).
- Cryptographic validity, expiration, issuer, and audience are verified statelessly.
- Replay attacks using revoked refresh tokens are neutralized by automatic session invalidation.
- Suspended accounts cannot log in or refresh tokens.
- Password reset foundation is operational with anti-enumeration protection.
- Unit test suite expanded from 28 to 38 tests (100% passing).

---

## 5. Immediate Next Steps (Discovery Phase Roadmap)

### Discovery Pipeline (HN + Remotive) in `lead_service`

Scope: Lean, production-grade discovery ingestion pipeline using Algolia HN Search API and Remotive API. Bypasses illegal private PII scraping in favor of live, high-intent public hiring signals.

- [ ] **TICKET-01: Build resilient API clients for HN Algolia & Remotive** *(Active)*
  - `httpx.AsyncClient`-based clients for Algolia HN Search API ("Who is hiring?") and Remotive API (software-dev jobs).
  - Pydantic models for raw response validation.
  - Resilience: `tenacity` exponential backoff, rate-limiting (429) backoff, explicit connection/read timeouts.
  - Comprehensive unit test suite with mocked HTTP responses (success, timeout, 429, malformed JSON).
- [ ] **TICKET-02: Data normalization + dedup layer**
  - Common `RawLead` schema (`company_name`, `description`, `source`, `source_url`, `posted_at`, `discovered_at`).
  - HN comment parser and Remotive mapper.
  - PostgreSQL `pg_trgm` extension & GIN trigram index on `company_name` for fuzzy deduplication (>0.85 similarity).
- [ ] **TICKET-03: Skill-matching scoring + persistence layer**
  - Configurable skill-keyword matching (0–100 score) with qualification threshold.
  - `Lead` SQLAlchemy model and Alembic migration (`status='new'`).
  - Repository pattern (`LeadRepository`).
- [ ] **TICKET-04: Celery orchestration**
  - `discover_leads` Celery task with idempotency and partial-failure isolation.
  - Celery Beat schedule and manual trigger endpoint (`POST /discovery/run`).
- [ ] **TICKET-05: Integration testing + polish**
  - End-to-end pipeline verification against live APIs, structured logging review, and documentation.

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


