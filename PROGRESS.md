# Leadforix — Development Progress & Session Handover

This file is the single source of truth for **where we left off, what has been completed, and what to do next**.
Any AI model or developer starting a new chat session should read this file first to resume immediately without re-exploring the whole repository.

---

## 1. Current Phase & Ticket

- **Current Ticket**: Day 02 — Docker & Infrastructure Foundation
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
- [x] **Shared & Infra Stubs**: `shared/` (`config`, `database`, `exceptions`, `logging`, `utils`) and `infrastructure/` (`database`, `messaging`, `redis`, `vector_db`).
- [x] **API Gateway (Traefik v3.5)**:
  - `infrastructure/api_gateway/traefik/traefik.yml` (ports 80 & 8080 dashboard)
  - `infrastructure/api_gateway/traefik/dynamic/routes.yml` configured with internal Docker service routing.
- [x] **Day 02 Stack & Infrastructure**:
  - Unified `Dockerfile` and `.dockerignore` configured with `python:3.14-slim` and `uv`.
  - Celery worker foundation (`infrastructure/messaging/celery_app.py`).
  - Centralized `infrastructure/docker-compose.yml` defining:
    - PostgreSQL 16 (`leadforix-postgres`, volume `postgres_data`, healthcheck)
    - Redis 7 (`leadforix-redis`, volume `redis_data`, healthcheck)
    - Qdrant v1.13.2 (`leadforix-qdrant`, volume `qdrant_data`)
    - Traefik v3.5 (`leadforix-traefik`, ports 80/8080)
    - 8 FastAPI microservices with code hot reload mounts
    - Celery worker foundation connected to Redis
  - Dedicated internal bridge network `leadforix-network` with Docker DNS.
  - Persistent named volumes verified across container restarts.

---

## 3. Key Decisions & Architectural Rules

1. **`main.py` Location**: The entry point belongs at `<service>/app/main.py` per Clean Architecture and `AGENTS.md` Section 5.
2. **Gateway Traefik Routing**: Traefik strips the `/api/<service>` prefix before forwarding requests to the service root via internal Docker service DNS (e.g. `/api/auth/health` -> `http://auth_service:8002/health`).
3. **No Premature Feature Work**: Do not implement auth logic, database migrations, LangGraph chains, or campaigns until the current ticket explicitly calls for it.
4. **Folder Naming**: Service folders follow `snake_case` (e.g. `workspace_service`).
5. **Infrastructure Centralization**: All compose files reside under `infrastructure/` per `AGENTS.md` Rule 9.

---

## 4. Current Status — Day 02 Done

**Day 02 Acceptance Criteria Achieved:**
- `docker compose up` builds and starts complete backend infrastructure (13 containers running).
- Internal DNS networking allows Traefik and services to communicate cleanly without exposing service ports.
- PostgreSQL, Redis, and Qdrant are accessible and passing healthchecks.
- Traefik routes `/api/<service>/health` correctly to all 8 microservices.
- Data persistence across container restarts verified for PostgreSQL and Redis.

---

## 5. Immediate Next Steps (Day 03 Preview)

Ready for **DAY-03** requirements.

## 6. Session Handover Instructions for New Chats

When the user starts a new chat and says:
> *"Let's continue where we left off"* or *"What's next?"*

The agent must:
1. Read this file ([PROGRESS.md](file:///e:/PERSONAL-PROJECTS/leadforix/PROGRESS.md)) and [AGENTS.md](file:///e:/PERSONAL-PROJECTS/leadforix/AGENTS.md).
2. Check section **4. Immediate Next Steps** above.
3. State the immediate task to the user and proceed with that single step. Do not re-explore the repository from scratch.
