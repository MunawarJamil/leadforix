# Leadforix

Leadforix is an AI-powered Sales Development Representative (SDR) platform that researches prospects, scores lead fit against a target profile, generates personalized outreach, and manages follow-up sequences using agentic AI. It's built as a production-oriented microservices backend, in the same problem space as tools like Clay, Instantly, and Apollo.

## Stack

- **API**: Python, FastAPI
- **AI/Agents**: LangChain, LangGraph, RAG
- **Data**: PostgreSQL, Qdrant (vectors), Redis
- **Async**: Celery
- **Infra**: Docker, Traefik (API gateway)

## Architecture

```
Client → Traefik (Gateway) → [Auth | Workspace | Lead | Campaign | Outreach]
                                        ↓
Redis → Celery → AI Worker
            ↓
LangGraph → LangChain → LLM / Qdrant (RAG) → PostgreSQL
```

Plus: Agent, Research, and Knowledge services.

## Services

| Service           | Responsibility                   | Route          | Port |
| ----------------- | -------------------------------- | -------------- | ---- |
| auth_service      | Auth, identity                   | /api/auth      | 8002 |
| workspace_service | Tenancy, workspace settings      | /api/workspace | 8008 |
| lead_service      | Lead/company/contact data        | /api/lead      | 8005 |
| campaign_service  | Campaigns & sequences            | /api/campaign  | 8003 |
| agent_service     | Agent orchestration              | /api/agent     | 8001 |
| research_service  | Prospect/company research        | /api/research  | 8007 |
| knowledge_service | Ingestion, embeddings, retrieval | /api/knowledge | 8004 |
| outreach_service  | Outreach & follow-ups            | /api/outreach  | 8006 |

Business logic lives in the owning service — not in `shared/`. Traefik strips the `/api/<service>` prefix before forwarding.

## Repo Structure

```
leadforix/
├── apps/services/<service_name>/
│   └── app/{api,application,domain,infrastructure}/ + main.py
├── shared/
├── infrastructure/api_gateway/   # Traefik config
├── tests/
└── pyproject.toml
```

- `api/` — routes & schemas
- `application/` — use cases
- `domain/` — business rules
- `infrastructure/` — DB & external integrations

No business logic in `main.py`.

## Local Development

Requires: Python 3.14+, Docker Desktop, Git, `uv`

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
uv sync
```

Run a service:

```bash
cd apps/services/<service_name>/app
python main.py
```

Start gateway (from repo root):

```bash
docker compose -f infrastructure/api_gateway/docker-compose.yml up -d
```

Gateway: `http://localhost` · Traefik dashboard: `http://localhost:8080`

> During this phase, FastAPI services run on the host; Traefik runs in Docker and reaches them via `host.docker.internal`. This will move to a shared Docker network once services are containerized.

## Engineering Principles

1. **Trace the flow before coding**: Client → Gateway → Service → Application → Domain → Infrastructure → DB. Async: API → Queue → Celery → Worker → Agent/Service → DB/Vector DB.
2. **Clean service boundaries** — prefer HTTP/events over cross-service imports.
3. **`shared/` stays generic** — no business logic.
4. **Each service owns its data.**
5. **Use AI components deliberately** — LangGraph for stateful multi-step workflows, LangChain for LLM/tool integration, RAG only when grounded retrieval is actually needed. Don't add agents/chains/vector search just because they're available.

## Planned AI Flow

```
Lead → Research → Context → RAG Retrieval → Fit Evaluation → LangGraph Agent
├─ Generate Outreach
└─ Decide Next Action
    ↓
Outreach → (Reply → update state | No reply → follow-up)
```

LangGraph checkpointing is key for maintaining context across interactions with a lead.

## For AI Coding Assistants

Before changing code: read `AGENTS.md`, check the current ticket, preserve existing architecture/naming, don't silently swap tech choices or implement future-day scope, explain architectural changes before making them broad.
