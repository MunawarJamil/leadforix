# Leadforix — Development Progress & Session Handover

This file is the single source of truth for **where we left off, what has been completed, and what to do next**.
Any AI model or developer starting a new chat session should read this file first to resume immediately without re-exploring the whole repository.

---

## 1. Current Phase & Ticket

- **Current Ticket**: Day 01 — Foundation & Gateway Routing
- **Status**: In Progress / Near Completion

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
  - `infrastructure/api_gateway/docker-compose.yml`
  - `traefik.yml` (ports 80 & 8080 dashboard)
  - `traefik/dynamic/routes.yml` configured with 8 routers, `stripPrefix` middlewares, and `host.docker.internal:<port>` load balancer servers.
- [x] **Initial Route Checks**: Workspace and research routes verified through Traefik.
- [x] **Scaffolding Fixes**: Corrected service titles in `research_service` and `agent_service`.

---

## 3. Key Decisions & Architectural Rules

1. **`main.py` Location**: The entry point belongs at `<service>/app/main.py` per Clean Architecture and `AGENTS.md` Section 5.
2. **Gateway Traefik Routing**: Traefik strips the `/api/<service>` prefix before forwarding requests to the service root (e.g. `/api/auth/health` -> `http://host.docker.internal:8002/health`).
3. **No Premature Feature Work**: Do not implement auth logic, database migrations, LangGraph chains, or campaigns until the current ticket explicitly calls for it.
4. **Folder Naming**: Service folders follow `snake_case` (e.g. `workspace_service`).

- [x] **Relocate `main.py`**: All services now have `main.py` inside `apps/services/<service>/app/main.py`.
- [x] **Directory Alignment**: Renamed `workspace_services` to `workspace_service`.
- [x] **Environment Variable Strategy**: Created root `.env.example` template and updated `.gitignore` to ignore `.env` files while preserving `.env.example`.
- [x] **Linting & Formatting Setup**: Added `ruff>=0.9.0` to `[dependency-groups] dev` and configured `[tool.ruff]` in `pyproject.toml`; ran `ruff format` and `ruff check` (all checks passed).
- [x] **Health Check Test Suite**: Added `pytest>=8.0.0` and `pythonpath = ["."]` in `pyproject.toml`; created `tests/unit/test_health.py` verifying all 8 services pass `/health` with `status: ok` and correct service name.

---

## 4. Current Status — Day 01 Done

**Day 01 Acceptance Criteria Achieved:**
- All 8 services start independently and pass `/health`.
- Monorepo structure, tooling (`uv`, `ruff`, `pytest`), and environment strategy established.
- Consistent Clean Architecture structure across all services.
- No premature business logic or duplicated code.

---

## 5. Immediate Next Steps (Day 02 Preview)

Ready for **DAY-02** requirements.

## 6. Session Handover Instructions for New Chats

When the user starts a new chat and says:
> *"Let's continue where we left off"* or *"What's next?"*

The agent must:
1. Read this file ([PROGRESS.md](file:///e:/PERSONAL-PROJECTS/leadforix/PROGRESS.md)) and [AGENTS.md](file:///e:/PERSONAL-PROJECTS/leadforix/AGENTS.md).
2. Check section **4. Immediate Next Steps** above.
3. State the immediate task to the user and proceed with that single step. Do not re-explore the repository from scratch.
