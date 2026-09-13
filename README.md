# Leadforix

Leadforix is an AI-powered client acquisition and SDR platform designed for **freelancers, individual job seekers, and tech agencies** to find high-intent clients and opportunities. Instead of scraping illegal personal PII for cold mass-emailing, Leadforix operates on **intent-driven public signals** (companies actively hiring on Hacker News, Remotive, engineering pain points) to power targeted, value-first outreach using agentic AI.

It is built as a production-oriented microservices backend with a phased build sequence:

1. **Phase 1 (Discovery & Lead Pipeline)**: Lean, production-grade discovery ingestion (Algolia HN API + Remotive API), trigram fuzzy deduplication, and skill-matching scoring.
2. **Phase 2 (Agentic AI & RAG Layer)**: Stateful multi-step agent workflows (LangGraph, LangChain, RAG, Qdrant) tested against live, real-world leads rather than synthetic mocks.
3. **Phase 3 (Agency Expansion)**: Multi-tenant workspace management, multi-client pipelines, team workflows, and full SDR follow-up sequencing.

## Stack

- **API**: Python, FastAPI
- **AI/Agents**: LangChain, LangGraph, RAG, LangSmith
- **Data**: PostgreSQL, Qdrant (vectors), Redis
- **Async**: Celery
- **Infra**: Docker, Traefik (API gateway)

## Architecture

```
Client / Scheduler → Traefik (Gateway) → [Lead | Auth | Workspace | Campaign | Outreach]
                                                ↓
Redis → Celery Beat → Discovery Pipeline (HN / Remotive)
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

## Discovery Pipeline (`lead_service`)

Leadforix's Discovery Pipeline ingests high-intent, public hiring signals from Hacker News ("Who is hiring?") and Remotive (software-dev opportunities). By focusing on publicly posted hiring needs rather than personal PII scraping, it eliminates GDPR/CAN-SPAM liability while surfacing live opportunities.

### Architecture & Data Flow

```
[Celery Beat Schedule] OR [POST /api/lead/discovery/run]
                     │
                     ▼
       Celery Task: discover_leads (Redis Mutex Lock)
                     │
           ┌─────────┴─────────┐  (Parallel / Bulkhead Fault Isolation)
           ▼                   ▼
     HN Client           Remotive Client
     (Tenacity Backoff)  (Tenacity Backoff)
           │                   │
       HN Parser        Remotive Mapper
           └─────────┬─────────┘
                     ▼
          HTML / Text Sanitizer
                     ▼
       DeduplicationService (Inverted Trigram Index + URL/ID Hash)
                     ▼
       SkillMatchingEngine (0–100 Score, Regex Boundaries, Title Multiplier)
                     ▼
           LeadRepository.save_bulk() → PostgreSQL
```

### Manual Discovery Trigger

Operators and authorized users (`OWNER`, `ADMIN`, `SALES_USER`) can trigger discovery on demand:

```bash
# 1. Trigger asynchronous discovery run
curl -X POST "http://localhost/api/lead/discovery/run" \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "hn_limit": 100,
    "remotive_limit": 100,
    "remotive_category": "software-dev",
    "save_only_qualified": false
  }'

# Response (HTTP 202 Accepted):
# {"task_id": "4b68e920-...", "status": "PENDING", "message": "Discovery workflow dispatched successfully."}

# 2. Check task execution status
curl -X GET "http://localhost/api/lead/discovery/status/4b68e920-..." \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

### Automated Scheduling (Celery Beat)

Celery Beat triggers `lead_service.discover_leads` periodically every 6 hours (`crontab(minute=0, hour="*/6")`).
- **Distributed Mutex Lock**: A Redis lock (`lock:leadforix:lead_discovery`) guarantees idempotency; overlapping runs automatically skip without duplicate API calls or database contention.
- **Bulkhead Isolation**: If one upstream provider encounters an outage or rate limit (HTTP 429), the other provider completes and persists its leads normally.

### Adding New Skill Keywords

Skill evaluation is configured in `apps/services/lead_service/app/application/scoring.py`. To introduce a new technology or domain skill:

```python
from apps.services.lead_service.app.application.scoring import SkillDefinition

# Add to DEFAULT_SKILL_PROFILES or create a custom SkillConfig:
SkillDefinition(
    canonical_name="Solana",
    weight=20,
    aliases=("solana", "sol", "anchor", "rust"),
)
```
- **Boundary-Safe Matching**: Handles punctuation in technology names (`C++`, `C#`, `.NET`, `Node.js`) without substring collisions.
- **Title Weight Multiplier**: Matches found in the job title receive a 2.0x weight bonus.
- **Qualification Gating**: By default, leads scoring $\ge 40$ are categorized as `QUALIFIED`.

### Running Verification Tests

```bash
# Run all unit tests
uv run pytest tests/unit/

# Run live and resilience integration tests
uv run pytest tests/integration/

# Generate test coverage report for lead_service (Acceptance: >= 80%)
uv run pytest --cov=apps/services/lead_service/app tests/
```

## For AI Coding Assistants

Before changing code: read `AGENTS.md`, check the current ticket, preserve existing architecture/naming, don't silently swap tech choices or implement future-day scope, explain architectural changes before making them broad.

