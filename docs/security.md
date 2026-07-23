# 🔒 Security Audit & Guidelines

## Summary

This document covers the security posture of the fintech-pipeline platform and recommendations for production hardening.

---

## Authentication & Authorization

### JWT Implementation

| Item | Status | Notes |
|---|---|---|
| JWT signing algorithm | ✅ HS256 | Symmetric — sufficient for single-service trust |
| Token expiry | ✅ 60 minutes | Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` |
| Secret from environment | ✅ | `JWT_SECRET_KEY` loaded via `os.getenv()` |
| Default fallback secret | ⚠️ MEDIUM | Fallback `"FINTECH_FRAUD_SECRET_KEY"` must be removed in production |

**Action:** Ensure `JWT_SECRET_KEY` is set in all production environments. The fallback is for development only.

### RBAC

| Role | Capabilities |
|---|---|
| `admin` | All endpoints including `/models/activate`, `/models/register` |
| `analyst` | Read-only: predictions, monitoring, drift |

### Password Storage

- Passwords are hashed using **bcrypt** (cost factor 12) via `passlib`
- No plaintext passwords stored
- Default users in `auth/users.py` use bcrypt hashes (not plaintext)

---

## CORS

| Item | Status | Notes |
|---|---|---|
| CORS restricted | ✅ | Origin controlled via `CORS_ALLOWED_ORIGIN` env var |
| Default (dev only) | ⚠️ | Defaults to `http://localhost:5173` if env var not set |

**Action for production:** Set `CORS_ALLOWED_ORIGIN=https://your-frontend-domain.com`

---

## Input Validation

| Item | Status | Notes |
|---|---|---|
| Pydantic schema validation (ML engine) | ✅ | All request bodies validated |
| SQL parameterization (Go gateway) | ✅ | Uses `lib/pq` with parameterized queries |
| Path traversal prevention | ✅ | File paths are constructed from registry, not user input |

---

## Docker Security

| Item | Status | Notes |
|---|---|---|
| Non-root user in containers | ✅ | `appuser` created in ingestion-gateway + ml-anomaly-engine Dockerfiles |
| Multi-stage builds | ✅ | Minimal runtime images |
| No secrets in Dockerfiles | ✅ | All secrets via environment variables |
| Healthchecks defined | ✅ | All services have Docker healthcheck |

---

## Secret Management

| Item | Status |
|---|---|
| `.env` in `.gitignore` | ✅ |
| No secrets committed | ✅ |
| `.env.example` has no real secrets | ✅ |

**Recommendation for production:** Use a secrets manager such as:
- AWS Secrets Manager
- HashiCorp Vault
- Docker Secrets (Swarm mode)

---

## Rate Limiting

- Rate limiting middleware is implemented in `ingestion-gateway/internal/middleware/rate_limit.go`
- Per-IP rate limiting via Redis

---

## Dependency Vulnerabilities

**Python (recommended scans):**
```bash
pip install pip-audit
pip-audit -r ml-anomaly-engine/requirements.txt
```

**Go (recommended scans):**
```bash
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...
```

**Node (recommended scans):**
```bash
cd fraud-dashboard
npm audit
```

---

## Security Recommendations

### Critical (Must Fix Before Production)

1. **Remove JWT fallback secret** in `auth/auth.py` — default value is predictable
2. **Rotate default user passwords** — change `admin` and `analyst` bcrypt hashes
3. **Set strong `POSTGRES_PASSWORD`** — current default is development-only

### Medium

4. **Add HTTPS** — use Nginx SSL termination or a load balancer with TLS
5. **Enable Redis password** — set `REDIS_PASSWORD` in production
6. **Set `CORS_ALLOWED_ORIGIN`** to production domain

### Low

7. **Add request size limits** in Nginx to prevent large payload DoS
8. **Implement refresh tokens** — current JWTs have no refresh mechanism
9. **Add brute-force protection** on the `/login` endpoint (rate limit by IP)
