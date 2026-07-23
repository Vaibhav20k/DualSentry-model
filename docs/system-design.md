# 🏗 System Design

## Design Principles

- **Event-driven** — Transactions flow through Kafka, decoupling ingestion from processing
- **Idempotent** — Duplicate transaction IDs are detected and rejected via Redis
- **Fail-safe** — Circuit breaker on ML client; rate limiter on gateway
- **Observable** — Prometheus metrics on all hot paths; structured audit logging
- **Extensible** — Model registry enables A/B testing and hot model swaps without downtime

---

## Component Responsibilities

### Fraud Dashboard (React + Vite)
- Role-based UI: admin sees model controls; analyst sees read-only views
- React Query for server-state management and automatic refetching
- Recharts for fraud trend visualization
- JWT stored in-memory (not localStorage) to prevent XSS token theft

### Ingestion Gateway (Go)
- **Single responsibility**: Accept, validate, and route transactions
- Publishes to Kafka topic (`transactions.raw`) for downstream consumers
- Calls ML Engine for synchronous fraud score (with circuit breaker for resilience)
- Persists transactions and fraud predictions to PostgreSQL
- Exposes Prometheus metrics on `/metrics`
- Redis-backed idempotency: duplicate `transaction_id` → immediate rejection
- Per-IP rate limiting via Redis

### ML Anomaly Engine (Python FastAPI)
- **Stateless inference**: loads model at startup from registry
- Feature validation with explicit error messages on malformed input
- JWT authentication gate on all prediction and admin endpoints
- Audit log every prediction with user context
- Drift detection: statistical comparison of live vs. training distributions
- Retraining pipeline: triggered on drift or manual invocation

### PostgreSQL
- Primary data store for transactions, fraud predictions, baselines, account history
- Initialized via `database/init-db.sql`
- Schema migrations tracked in `database/migrations/`

### Redis
- Idempotency store: `transaction_id → seen` with TTL
- Rate limiter: per-IP counters with sliding window

### Kafka + Zookeeper
- Event broker for transaction events
- Topic: `transactions.raw` (8 partitions, replication factor 1 for dev)
- Consumer group for downstream processing (streaming-consumer)

### Transaction Simulator (Go)
- Generates realistic fraud/legitimate transaction mix
- Configurable TPS via `TPS` environment variable
- Posts directly to the Ingestion Gateway HTTP API

---

## Request Flow: Transaction Submission

```
Client (Dashboard or Simulator)
  │
  │  POST /api/transactions
  ▼
Nginx Reverse Proxy
  │  /api/ → ingestion-gateway:8080
  ▼
Go Ingestion Gateway
  ├── 1. Parse & validate request body
  ├── 2. Check Redis idempotency key
  ├── 3. Persist transaction to PostgreSQL
  ├── 4. Publish to Kafka (async)
  ├── 5. Call ML Engine /predict (sync, circuit-breaker protected)
  ├── 6. Persist fraud prediction to PostgreSQL
  └── 7. Return response to client
```

---

## Request Flow: ML Prediction

```
Go Gateway / Direct Client
  │
  │  POST /predict + Bearer token
  ▼
FastAPI ML Engine
  ├── 1. Verify JWT
  ├── 2. Validate request schema (Pydantic)
  ├── 3. Run feature validation
  ├── 4. Load active model from registry
  ├── 5. Transform features via preprocessor
  ├── 6. XGBoost inference
  ├── 7. Apply optimal threshold
  ├── 8. Log prediction to audit log
  └── 9. Return PredictionResponse
```

---

## Scalability Considerations

| Concern | Current Approach | Production Path |
|---|---|---|
| Gateway throughput | Single instance, Go net/http | Horizontal scaling behind Nginx |
| ML inference | Single process | Multiple uvicorn workers or separate inference service |
| Database | Single PostgreSQL | Read replicas for dashboard queries |
| Kafka partitions | 8 partitions | Match to consumer parallelism |
| Model loading | In-process at startup | Model serving via Triton or TorchServe |

---

## Trade-offs

| Decision | Why |
|---|---|
| Sync ML call in gateway | Simplicity; fraud score returned in same response |
| JSON model registry | Suitable for portfolio scale; production would use MLflow |
| In-memory user store | Simple for demo; production would use a database |
| Single-node Kafka | Dev/portfolio; production needs 3+ brokers with replication |
