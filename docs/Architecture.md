# 📐 Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client Layer                                   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              Fraud Dashboard (React + TypeScript + Vite)         │   │
│   │                        fraud-dashboard:3001                      │   │
│   └───────────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────────────│─────────────────────────────────────┘
                                    │ HTTP REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Proxy Layer                                    │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Nginx Reverse Proxy (:80)                     │   │
│   │       /api/* → ingestion-gateway    /ml/* → ml-engine           │   │
│   └─────────────┬──────────────────────────────┬────────────────────┘   │
└─────────────────│──────────────────────────────│────────────────────────┘
                  │                              │
                  ▼                              ▼
┌──────────────────────────────┐  ┌─────────────────────────────────────┐
│    Ingestion Gateway (Go)    │  │     ML Anomaly Engine (Python)       │
│                              │  │                                      │
│  • REST HTTP (:8080)         │  │  • FastAPI (:8000)                   │
│  • gRPC (:50051)             │  │  • XGBoost inference                 │
│  • Kafka producer            │  │  • Model registry + hot-swap         │
│  • Redis idempotency         │  │  • JWT RBAC (admin/analyst)          │
│  • Rate limiting             │  │  • Audit logging                     │
│  • Circuit breaker → ML      │  │  • Drift detection                   │
│  • Prometheus metrics        │  │  • Retraining pipeline               │
└──────────────┬───────────────┘  └──────────────┬──────────────────────┘
               │                                  │
               ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Layer                                     │
│                                                                          │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────┐   │
│   │ PostgreSQL  │   │    Redis    │   │   Apache Kafka + Zookeeper  │   │
│   │   (:5432)   │   │   (:6379)   │   │   (:9092 / :2181)           │   │
│   │             │   │             │   │   topic: transactions.raw   │   │
│   │ • tx data   │   │ • idempoten │   │   8 partitions              │   │
│   │ • fraud     │   │   -cy store │   │                             │   │
│   │   predicts  │   │ • rate limit│   └─────────────────────────────┘   │
│   │ • baselines │   └─────────────┘                                      │
│   └─────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Observability Layer                               │
│                                                                          │
│   ┌─────────────────────┐         ┌─────────────────────────────────┐   │
│   │  Prometheus (:9090) │────────▶│     Grafana (:3000)             │   │
│   │  Scrapes:           │         │   Dashboards & Alerts            │   │
│   │  - ingestion-gw     │         └─────────────────────────────────┘   │
│   │  - ml-engine        │                                                │
│   └─────────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Service Inventory

| Service | Technology | Port | Purpose |
|---|---|---|---|
| fraud-dashboard | React 18 + Vite | 3001 | User interface |
| ingestion-gateway | Go 1.22 | 8080 (HTTP), 50051 (gRPC) | API gateway, event ingestion |
| ml-anomaly-engine | Python 3.11 + FastAPI | 8000 | Fraud inference + model registry |
| transaction-simulator | Go 1.22 | — | Load generator |
| postgres | PostgreSQL 16 | 5432 | Primary database |
| redis | Redis 7 | 6379 | Cache, idempotency, rate limiting |
| kafka | Confluent Kafka 7.5 | 9092 | Event streaming |
| zookeeper | Confluent Zookeeper 7.5 | 2181 | Kafka coordination |
| nginx | Nginx 1.27 | 80 | Reverse proxy |
| prometheus | Prometheus | 9090 | Metrics collection |
| grafana | Grafana | 3000 | Metrics visualization |

---

## Data Flow

### Transaction Ingestion

```
Simulator / Client
    │ POST /api/transactions
    ▼
Ingestion Gateway
    ├── Validate payload
    ├── Deduplicate (Redis idempotency)
    ├── INSERT transaction → PostgreSQL
    ├── Publish event → Kafka transactions.raw
    ├── POST /predict → ML Engine
    ├── INSERT fraud prediction → PostgreSQL
    └── Return result
```

### ML Prediction

```
Ingestion Gateway
    │ POST /predict (JWT)
    ▼
ML Anomaly Engine
    ├── Verify JWT
    ├── Validate features (Pydantic + custom validator)
    ├── Load active model from registry
    ├── Transform features via preprocessor
    ├── XGBoost inference → fraud probability
    ├── Apply optimal threshold → is_fraud
    ├── Log to audit log
    └── Return PredictionResponse
```

---

## Network Topology (Docker Compose)

All services communicate on a single Docker bridge network: `fintech-network`.

Services expose ports **only** where necessary:
- `postgres`, `redis`, `kafka`, `zookeeper` — no host ports exposed (internal only)
- `ingestion-gateway` — exposed internally via Nginx
- `ml-anomaly-engine` — port 8000 exposed for direct dev access
- `nginx` — port 80 exposed as the single public entry point
- `prometheus` — port 9090 for scraping
- `grafana` — port 3000 for dashboards
- `fraud-dashboard` — port 3001

---

## Repository Layout

```
fintech-pipeline/
├── .github/workflows/ci.yml      # CI/CD pipeline
├── fraud-dashboard/               # Frontend (React + Vite)
├── ingestion-gateway/             # Go API Gateway
├── ml-anomaly-engine/             # Python ML Engine
├── transaction-simulator/         # Go load generator
├── database/                      # SQL schema + migrations
├── nginx/                         # Reverse proxy config
├── observability/                 # Prometheus + Grafana
├── docs/                          # Extended documentation
├── docker-compose.yml
└── .env.example
```