# AGENTS.md — Leadforix Engineering Rules

Read this file fully before making any change. Multiple AI models work on this repo — this file is the shared source of truth so behavior stays consistent across them.

## 0. Project

Leadforix is an AI-powered SDR platform (prospect research, lead scoring, personalized outreach, follow-up sequencing) built as a production-oriented Python microservices backend. Built incrementally via day-based tickets. Priority right now: correctness, architecture, and request/data flow — not new functionality beyond the current ticket.

**Stack**: FastAPI, PostgreSQL, Qdrant, Redis, Celery, LangChain, LangGraph, RAG, Docker, Traefik.

## 1. Golden Rule

**Do not guess the architecture.** Before any meaningful change:

1. Read this file and `PROGRESS.md` to resume state without re-scanning the whole repository.
2. Inspect the existing repo structure and the relevant service.
3. Identify the current ticket/day from `PROGRESS.md`.
4. Trace the request/data flow.
5. Make the smallest change that satisfies the requirement.
6. Verify the result.

If a request conflicts with an existing architectural decision, **state the conflict and ask before changing the architecture** — don't silently override it.

## 2. Working Style & Engineering Guidelines

- **Step-by-step only**: Work incrementally, one step at a time. Never do everything at once or jump ahead to future tickets.
- **No autonomous code modifications unless explicitly requested**: Do not write or edit codebase files directly unless the user explicitly requests you to do the implementation. First, understand the task carefully, explain the task and data flow concisely in chat with a short plan, and propose Step 1. Wait for the user's approval (`done`). Then tell the user what to do, where, and the short rationale why.
- **Senior Architect Quality**: Code must be mature, highly scalable, and production-grade for multi-tenant high-throughput systems.
- **Educational Annotations & Design Patterns**: When providing code snippets, add concise comments explaining what functions/classes do, explicitly identifying engineering principles and design patterns (e.g., Abstraction, Encapsulation, Dependency Injection, Repository, Factory, Singleton) to teach foundational software engineering.
- **Step 0 Branch Suggestion**: When starting any new task, Step 0 is always to suggest creating a new branch in chat (format: `feat/lf-XX-short-description`, e.g., `feat/lf-03-database-foundations`). Do not create it directly; suggest the exact git command for the user to run.
- **Meaningful Commit Messages**: After completing the implementation and verification of a task, always provide a proper, meaningful conventional commit message summarizing the changes.
- **Session Handover & Memory Updates**: When finishing a task or pausing for later, update `PROGRESS.md`, `AGENTS.md`, and the Mem0 MCP memory.


## 3. Request Flow

```
Client → Traefik → {auth, workspace, lead, campaign, agent, research, knowledge, outreach}_service
```

Async/AI flow:

```
FastAPI Service → Redis/Queue → Celery Worker → Agent/LangGraph → {LangChain, LLM, Qdrant/RAG} → PostgreSQL
```

Traefik is the single external gateway. Internal services are not public endpoints.

## 4. Service Boundaries (do not cross without an explicit decision)

| Service           | Owns                                        |
| ----------------- | ------------------------------------------- |
| auth_service      | authN/authZ                                 |
| workspace_service | tenancy, membership, settings               |
| lead_service      | leads, companies, contacts, lifecycle       |
| campaign_service  | campaign config, sequences, execution state |
| agent_service     | agent orchestration/behavior                |
| research_service  | prospect/company research                   |
| knowledge_service | ingestion, chunking, embeddings, retrieval  |
| outreach_service  | outreach messages, delivery, follow-ups     |

Prefer `Service A → Service B API/event` over `Service A → Service B's database tables`, ever.

## 5. Service Structure (every service)

```
<service>/app/{api, application, domain, infrastructure}/ + main.py
<service>/test/
```

- `api/` — routes, request/response models, DI wiring. No business logic.
- `application/` — use cases, orchestration between domain and infrastructure.
- `domain/` — business rules, kept framework/infra-independent where practical.
- `infrastructure/` — DB, Redis, Qdrant, Celery, external APIs.
- `main.py` — bootstrap only, never domain logic.

## 6. Python / Tooling

- Monorepo (not a single package) — root `pyproject.toml` reflects this.
- Dependency management: `uv sync`. Don't introduce another package manager without explicit approval.
- Don't create root-level packages just for import convenience.

## 7. FastAPI & Ports

| Service           | Port | Gateway path   |
| ----------------- | ---- | -------------- |
| agent_service     | 8001 | /api/agent     |
| auth_service      | 8002 | /api/auth      |
| campaign_service  | 8003 | /api/campaign  |
| knowledge_service | 8004 | /api/knowledge |
| lead_service      | 8005 | /api/lead      |
| outreach_service  | 8006 | /api/outreach  |
| research_service  | 8007 | /api/research  |
| workspace_service | 8008 | /api/workspace |

Every service exposes `/health`. Traefik strips the `/api/<service>` prefix before forwarding (e.g. `/api/workspace/health` → `workspace_service:/health`). Ports are dev-only and will change once containerized.

## 8. Traefik

- Currently runs in Docker; FastAPI services run on host → reached via `host.docker.internal` (e.g. `http://host.docker.internal:8008`).
- Once services are containerized: switch to Docker network + service DNS names (e.g. `http://workspace_service:8008`), not host ports.

## 9. Docker

- Infra (Postgres, Redis, Qdrant, Traefik, Celery workers) runs in Docker — never require manual host installs.
- Keep all compose/config under `infrastructure/`. No stray compose files elsewhere.

## 10. Database

- PostgreSQL is primary. Ownership per service is explicit — no arbitrary cross-service DB access just because it's technically reachable.
- Schema design follows domain boundaries.

## 11. Redis / Celery

- Redis is infrastructure only, never business logic.
- Celery is for genuinely async/background work: research jobs, enrichment, embedding generation, long-running AI workflows, outreach scheduling, follow-ups.
- Don't wrap simple synchronous operations in Celery.

## 12. LangChain / LangGraph / RAG / Qdrant

- **LangChain** — reusable LLM/tool/retrieval integrations.
- **LangGraph** — stateful, multi-step agent workflows.
- **RAG** — only when the model needs grounded retrieval from stored knowledge.
- **Qdrant** — vector/semantic retrieval backing RAG.
- Don't add an agent, chain, or RAG pipeline just because it's available — use the simplest thing that solves the actual requirement.

## 13. Agent State

Conceptual flow: `Lead → Research → Context → Knowledge Retrieval → LangGraph {Evaluate, Personalize, Draft, Decide} → Outreach → (Reply → update state | No reply → Follow-up)`.

Checkpointing/state persistence is an architectural concern to design up front, not bolt on later.

## 14. `shared/`

Only for genuinely reusable, non-domain code: API contracts, technical utilities, logging primitives, shared config, justified common error types.

Never: lead/campaign business logic, or anything used to bypass service boundaries. If it belongs to one domain, it stays in that service.

## 15. Naming

`snake_case` service and module names (`auth_service`, `lead_service`, etc.). Don't introduce `auth-service`/`authService`/`AuthService` unless an external tool/protocol requires it.

## 16. Config & Secrets

Never hard-code API keys, credentials, DB URLs, or tokens. Use environment variables. Never commit real secrets — use placeholders (`DATABASE_URL=`, `REDIS_URL=`, `OPENAI_API_KEY=`).

## 17. Errors & Logging

- Never leak internal implementation details in public API responses.
- Never swallow exceptions silently.
- Background jobs log: job type, entity ID, failure reason, retry state — never secrets.

## 18. Testing

- Service tests live in `<service>/test/`; cross-service/integration tests live in root `tests/`.
- Test behavior, not implementation details.
- Gateway changes: verify the full `Client → Traefik → service → endpoint` flow, not just config.

## 19. Documentation

Update `README.md` when structure, services, architecture, setup, routing, or infra change. Update this file when engineering rules/constraints change. Docs must never describe an architecture that no longer exists.

## 20. Git Discipline

Small, focused commits (`feat(auth): add health endpoint`, `chore(gateway): configure workspace route`). No unrelated refactors mixed into feature work. No repo-wide reformatting as a side effect. Never delete working code without understanding why it's there.

## 21. Multi-Model Discipline

**Always**: read this file, inspect existing code, preserve established decisions, check the current ticket, make minimal changes, verify.

**Never**: treat the repo as blank, replace the architecture with a "more familiar" pattern, introduce a new framework without approval, rename services casually, move folders without a concrete reason, auto-implement future roadmap items, overwrite working config without checking it.

The current repository state is the source of truth, even over what a previous model may have intended.

## 22. Decision Priority (when in conflict)

1. Explicit current ticket/task
2. Existing repo architecture
3. This file (AGENTS.md)
4. README.md
5. Established technology choices
6. General best practices

Never silently pick one — surface the conflict and ask when it matters.

## 23. Definition of Done

`Requirement understood → correct service identified → implementation → tests/validation → request/data flow verified → docs updated if needed → done.`

For infra changes: verify actual runtime behavior, not just config syntax.

## 24. Current Status — Day 04 Complete

**Before inspecting the repo, always read PROGRESS.md first**. It tells you exactly which service is in scope — do not scan the full monorepo unless the current task explicitly requires cross-service work.

**Done**: Monorepo structure & Clean Architecture for all 8 microservices, Docker Compose stack, async PostgreSQL & Alembic migrations, unified exceptions & structured logging, complete authentication service (`auth_service`) with salted bcrypt password hashing, JWT access token & opaque refresh token pair, single-use token rotation, token revocation/logout, RBAC roles (`OWNER`, `ADMIN`, `SALES_USER`, `AGENT`), protected endpoint dependencies (`get_current_user`, `require_roles`), and full unit test coverage (28 passed).

**Next**: Day 05 ticket.


