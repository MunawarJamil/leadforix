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

### Running with Docker (Selective vs Full Stack)

We use Docker Compose profiles so you don't have to run all 8 services simultaneously.

**1. Run Only What You Need (Core Infra + Specific Service)**:
```bash
# Start Traefik, Postgres, Redis + Auth Service only
docker compose -f infrastructure/docker-compose.yml up -d traefik auth_service

# Start any other service on demand (e.g. Lead Service)
docker compose -f infrastructure/docker-compose.yml up -d traefik lead_service
```

**2. Start Full Stack (All 8 Services + Celery + Infra)**:
```bash
docker compose -f infrastructure/docker-compose.yml --profile full up -d
```

**3. Stop Services**:
```bash
# Stop running services
docker compose -f infrastructure/docker-compose.yml down

# If started with --profile full:
docker compose -f infrastructure/docker-compose.yml --profile full down
```

**4. Useful Docker Commands**:
```bash
# View live logs for a service
docker logs -f leadforix-auth-service

# Inspect Postgres tables interactively via psql
docker exec -it leadforix-postgres psql -U leadforix -d leadforix

# Run database migrations from host
uv run alembic upgrade head
```

**Access URLs & Ports**:
- Gateway (Traefik): `http://localhost` (port 80)
- Auth Swagger Docs: `http://localhost/api/auth/docs`
- Traefik Dashboard: `http://localhost:8080`
- Postgres (Host mapped): `localhost:5433` (User: `leadforix`, DB: `leadforix`)
- Redis: `localhost:6379` · Qdrant: `http://localhost:6333`

> All services and infrastructure run containerized on the internal `leadforix-network` bridge network. Traefik serves as the single external gateway and routes to services via internal Docker DNS. Mounted volumes allow local hot reloading during development.

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
