# Discovery Pipeline Architecture — Intent-Driven Lead Ingestion

## 1. Context & Motivation

Traditional outbound SDR platforms often rely on web scraping personal PII (private cell phone numbers, personal emails, residential addresses). This approach incurs:
1. **Severe Legal & Compliance Violations**: Non-compliance with GDPR Article 6/14, CAN-SPAM, and state consumer privacy acts.
2. **Low Conversion & High Risk**: Unsolicited cold outreach to individuals without intent triggers domain blacklisting, high bounce rates, and spam-trap penalties.

Leadforix shifts the discovery paradigm to **public intent signals**:
- Reaching out only to companies and engineering leaders that have **publicly and deliberately broadcast an active hiring or contractor requirement**.
- Beginning with **freelancers, individual job seekers, and tech agencies**, targeting real engineering needs before scaling to multi-tenant SDR workflows.

---

## 2. Ingestion Sources

| Source | Protocol / Endpoint | Signal Type | Auth / Tier |
| :--- | :--- | :--- | :--- |
| **Algolia HN Search API** | `https://hn.algolia.com/api/v1/` | Monthly *"Ask HN: Who is hiring?"* & *"Seeking freelancer?"* threads with direct founder / hiring manager comments. | Public / Free |
| **Remotive API** | `https://remotive.com/api/remote-jobs?category=software-dev` | Structured JSON feed of remote software engineering positions with company, location, tags, and job descriptions. | Public / Free |

*(Note: Google Places API and automated web enrichment are deferred to later phases).*

---

## 3. High-Level Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│ Celery Beat / Manual Trigger (POST /discovery/run)           │
└──────────────────────────────┬───────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     [HnAlgoliaClient]                 [RemotiveClient]
      - httpx.AsyncClient               - httpx.AsyncClient
      - tenacity exponential backoff    - tenacity exponential backoff
      - 429 rate limit backoff          - 429 rate limit backoff
               │                               │
               └───────────────┬───────────────┘
                               ▼
            ┌────────────────────────────────────┐
            │ Data Normalization Layer           │
            │  - HN Free-Text Parser             │
            │  - Remotive Structured Mapper      │
            │  - Output: RawLead Schemas         │
            └──────────────────┬─────────────────┘
                               ▼
            ┌────────────────────────────────────┐
            │ PostgreSQL Trigram Deduplication   │
            │  - pg_trgm GIN Trigram Index       │
            │  - similarity(company_name) > 0.85 │
            │  - Discards existing duplicates    │
            └──────────────────┬─────────────────┘
                               ▼
            ┌────────────────────────────────────┐
            │ Skill Matching & Scoring Engine    │
            │  - Pure deterministic scoring      │
            │  - Configurable keyword weights    │
            │  - Score >= Threshold (e.g. >= 40) │
            └──────────────────┬─────────────────┘
                               ▼
            ┌────────────────────────────────────┐
            │ Persistence (LeadRepository)       │
            │  - SQLAlchemy 2.0 Async Session    │
            │  - Status: 'new'                   │
            │  - Ready for Agent / Outreach flow │
            └────────────────────────────────────┘
```

---

## 4. Resilience & Distributed Systems Patterns

1. **Partial-Failure Isolation**:
   - If the Algolia HN endpoint experiences an outage, the Remotive pipeline continues unaffected, and vice versa.
   - Failures are logged with structured context without aborting the entire Celery task.
2. **Tenacity Exponential Backoff & Jitter**:
   - Network timeouts, 5xx server errors, and connection drops trigger up to 3 retry attempts with randomized exponential backoff to avoid thundering-herd problems.
3. **HTTP 429 Rate-Limit Handling**:
   - Standard 429 responses inspect `Retry-After` headers where available or back off exponentially rather than crashing.
4. **Trigram Fuzzy Deduplication (`pg_trgm`)**:
   - Ingesting from multiple sources naturally yields company name variations (e.g., *"Acme Inc"*, *"Acme, Inc."*, *"Acme"*).
   - PostgreSQL's `pg_trgm` extension allows fast indexed trigram comparison directly in the database without memory-heavy in-process string matching.
5. **Idempotency**:
   - Each discovery task run tracks a batch identifier. Re-running the pipeline on the same day is safe and produces 0 duplicate leads.

---

## 5. Service Placement

Per the Service Boundaries defined in `AGENTS.md`:
- The discovery pipeline lives inside **`lead_service`** under `app/infrastructure/clients/`, `app/domain/`, and `app/application/`.
- Once leads are qualified and stored, downstream services (`agent_service`, `outreach_service`) consume them via standard APIs and event triggers.
