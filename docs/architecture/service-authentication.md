# Service Authentication & Authorization Architecture

## 1. Architectural Overview

Leadforix follows a microservice architecture behind the Traefik API Gateway. To ensure high throughput, fault tolerance, and strict service isolation, **downstream microservices never query `auth_service`'s database directly to authenticate requests**.

Instead, inter-service authentication relies on **Stateless Cryptographic Token Verification**:
- `auth_service` mints cryptographically signed RFC 7519 JSON Web Tokens (JWT).
- Downstream services (`workspace_service`, `lead_service`, `campaign_service`, `agent_service`, `research_service`, `knowledge_service`, `outreach_service`) verify incoming tokens locally in-memory using `shared.security`.

---

## 2. Token Specification & Claims

### Access Token Characteristics
- **Standard**: RFC 7519 (JSON Web Token)
- **Signature Algorithm**: HMAC-SHA256 (`HS256`)
- **Lifetime**: 15 minutes (short-lived to minimize exposure of leaked tokens)
- **Audience (`aud`)**: `"leadforix-api"`
- **Issuer (`iss`)**: `"leadforix-auth"`

### Standard Claim Payload
```json
{
  "sub": "b2c15147-1959-4d6a-86c4-b9c1d09e5b0a",
  "email": "user@example.com",
  "role": "SALES_USER",
  "workspace_id": "9a385f9e-2144-42b7-a36c-2f928c039ab1",
  "type": "access",
  "iss": "leadforix-auth",
  "aud": "leadforix-api",
  "iat": 1757376000,
  "exp": 1757376900
}
```

| Claim | Type | Required | Description |
|---|---|---|---|
| `sub` | UUID string | Yes | Unique User ID of authenticated subject |
| `email` | String | Yes | Corporate email address |
| `role` | String | Yes | RBAC Role (`OWNER`, `ADMIN`, `SALES_USER`, `AGENT`) |
| `workspace_id` | UUID string \| null | No | Active tenant workspace context if present in token |
| `type` | String | Yes | Must be `"access"` (defeats token substitution attacks) |
| `iss` | String | Yes | Expected issuer (`"leadforix-auth"`) |
| `aud` | String | Yes | Expected audience (`"leadforix-api"`) |
| `iat` | Integer | Yes | Issued-at epoch timestamp |
| `exp` | Integer | Yes | Expiration epoch timestamp |

---

## 3. Downstream Service Consumption Guide

Every microservice uses the reusable abstractions exported by `shared.security`:

### 3.1 Authenticating Requests Statelessly
```python
from fastapi import APIRouter, Depends
from shared.security import get_current_user, UserPrincipal

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("")
async def list_leads(current_user: UserPrincipal = Depends(get_current_user)):
    # Authenticated without database round-trip
    return {
        "caller_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }
```

### 3.2 Enforcing Role-Based Access Control (RBAC)
Use `require_roles(...)` higher-order dependency:
```python
from fastapi import APIRouter, Depends
from shared.security import require_roles, UserPrincipal

router = APIRouter(tags=["Admin"])


@router.delete(
    "/campaigns/{campaign_id}",
    dependencies=[Depends(require_roles("OWNER", "ADMIN"))],
)
async def delete_campaign(campaign_id: str):
    return {"status": "deleted"}
```

### 3.3 Resolving Multi-Tenant Workspace Context
Multi-tenant operations resolve workspace context using priority ordering:
1. Explicit `workspace_id` claim in JWT.
2. `X-Workspace-ID` HTTP header passed by client during workspace switching.
3. Rejects with HTTP 403 Forbidden if neither is present.

```python
from uuid import UUID
from fastapi import APIRouter, Depends
from shared.security import require_workspace

router = APIRouter(tags=["Leads"])


@router.post("")
async def create_lead(
    workspace_id: UUID = Depends(require_workspace),
):
    # Guaranteed valid UUID for tenant isolation
    return {"workspace_id": str(workspace_id)}
```

---

## 4. Security Hardening & Session Guarantees

1. **Single-Use Token Rotation**: Every refresh token exchange revokes the old token and issues a new pair.
2. **Automatic Token Family Reuse Detection (RFC 6819 §5.2.2.3)**: If an already-revoked refresh token is re-submitted, the server identifies a replay/theft breach and revokes **all** active sessions for that user ID.
3. **Account Lifecycle Handling**: Accounts with `status: SUSPENDED` or `status: PENDING_VERIFICATION` are immediately rejected during login and token refresh.
4. **Password Reset Defense-in-Depth**:
   - `POST /password-reset/request` is timing-safe and enumeration-resistant (always returns 200).
   - Reset tokens are CSPRNG strings; only SHA-256 hashes are persisted.
   - Reset tokens expire in 15 minutes and are strictly single-use.
   - Confirming a password reset immediately revokes all active refresh tokens across all client devices.
5. **Password Complexity**: Enforces length 8–128 chars, lowercase, uppercase, digit, and special character.
