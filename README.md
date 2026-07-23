<div align="center">

# 🛡️ DualSentry

### *Enterprise-Grade, Real-Time AI Financial Fraud Detection Platform*

[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=for-the-badge&logo=activemq)](https://github.com/Vaibhav20k/fintech-pipeline)
[![Go Version](https://img.shields.io/badge/Go-1.22-00ADD8?style=for-the-badge&logo=go)](https://golang.org)
[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![React Version](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose_v2-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

<br />

**DualSentry** is a high-performance, distributed financial fraud detection system that ingests transaction streams, evaluates fraud risk using **XGBoost** ML models in **< 50ms**, and delivers real-time analytics through an interactive React dashboard.

[⚡ Quick Start](#-quick-start) · [🏗️ Architecture](#️-architecture) · [🌟 Key Highlights](#-engineering-highlights) · [📡 API Reference](#-api-reference) · [📚 Documentation Hub](#-documentation-hub)

<br />

---

### 📷 Platform Previews

| **React Fraud Operations Dashboard** | **Prometheus & Grafana Observability** |
|:---:|:---:|
| ![Dashboard Preview](https://raw.githubusercontent.com/Vaibhav20k/fintech-pipeline/main/docs/assets/dashboard_preview.png) | ![Grafana Preview](https://raw.githubusercontent.com/Vaibhav20k/fintech-pipeline/main/docs/assets/grafana_preview.png) |
| *Real-time transaction stream, risk probability scoring, and KPI metrics* | *Prometheus metric scrapers, latency histograms, and engine telemetry* |

| **Model Registry & Hot-Swapping** | **System Architecture Blueprint** |
|:---:|:---:|
| ![Model Registry Preview](https://raw.githubusercontent.com/Vaibhav20k/fintech-pipeline/main/docs/assets/registry_preview.png) | ![Architecture Preview](https://raw.githubusercontent.com/Vaibhav20k/fintech-pipeline/main/docs/assets/architecture_preview.png) |
| *Zero-downtime model activation with drift monitoring statistics* | *End-to-end event streaming, API Gateway, and database flow* |

---

</div>

<br />

## 📊 Repository At a Glance

| Dimension | Specification |
|---|---|
| **Core Languages** | Go 1.22, Python 3.11, TypeScript 5.0, SQL, HTML5/CSS3 |
| **Microservices** | Go API Gateway, Python FastAPI ML Engine, React Dashboard, Go Load Simulator |
| **Inference SLA** | **< 50ms p95 latency** for real-time risk evaluation |
| **Data Streaming** | Apache Kafka (8 topic partitions) + Zookeeper coordination |
| **Storage & Caching** | PostgreSQL 16 (Primary DB) + Redis 7 (Idempotency & Rate Limiting) |
| **Security & Auth** | JWT Bearer Authentication, Granular RBAC (Admin / Analyst), bcrypt cost 12 |
| **Observability** | Prometheus metrics exporter + Grafana Dashboards + Structured Audit Logging |
| **CI/CD & DevOps** | GitHub Actions Pipeline + Multi-stage Docker Builds + Nginx Reverse Proxy |

---

## ❓ Why DualSentry?

Financial institutions process millions of transactions daily, facing persistent threats from modern automated fraud vectors. 

### The Problem
- **Rules Are Static**: Traditional rule-based engines fail to detect novel fraud patterns and produce high false-positive rates, degrading legitimate user experience.
- **Latency Is Critical**: Fraud evaluation must occur synchronously within payment authorization windows (< 100ms total budget).
- **Data Drift**: Fraud behavior evolves over time; ML models decay if not continuously monitored against statistical drift.

### The DualSentry Approach
DualSentry combines an **event-driven Go gateway** for high-throughput ingestion with a **Python FastAPI inference engine** running an optimized **XGBoost classifier**. It enforces idempotency via Redis, queues raw transactions to Kafka for downstream consumers, statistical drift detection (PSI/Chi-sq), and supports **zero-downtime model hot-swapping** via a centralized model registry.

---

## 💡 Engineering Highlights

Key technical implementations featured in this repository:

- 🚀 **Sub-50ms Inference**: Optimized FastAPI predictor pipeline using pre-fitted transformers and XGBoost probability thresholding.
- ⚡ **Go Concurrency & Resilience**: Go HTTP/gRPC gateway leveraging worker patterns, Redis sliding-window rate limiting, and circuit breakers for downstream ML fallbacks.
- 🔄 **Kafka Distributed Streaming**: Non-blocking transaction publishing to Kafka (`transactions.raw`) for async event processing.
- 🛡️ **Enterprise Security & RBAC**: JWT Bearer token verification with strict Role-Based Access Control (Admin vs. Analyst role enforcement).
- 🔄 **Zero-Downtime Model Registry**: Dynamic model manager enabling live hot-swapping of active ML models without microservice restarts.
- 📈 **Automated Drift & Retraining**: Drift runner calculating Population Stability Index (PSI) and triggering containerized model retraining pipelines.
- 📊 **Full-Stack Observability**: Native Prometheus metrics (`http_requests_total`, `http_request_duration_seconds`) scraped across services into Grafana dashboards.

---

## ⚡ Grouped Feature Matrix

<details open>
<summary><b>🤖 AI & Machine Learning</b></summary>

- **XGBoost Fraud Classifier**: Trained on IBM Financial AML dataset achieving ~97% accuracy and ~0.89 F1-Score.
- **Dynamic Model Registry**: Centralized JSON-backed registry tracking versioning, accuracy metrics, and active model flags.
- **Zero-Downtime Hot-Swapping**: Switch active model versions live via authenticated Admin API endpoints.
- **Statistical Drift Monitoring**: Automatic calculation of Population Stability Index (PSI) to detect feature distribution shifts.
- **Automated Retraining Pipeline**: Modular pipeline for re-extracting dataset baselines, fitting XGBoost models, and updating registry artifacts.
</details>

<details open>
<summary><b>⚡ Backend & Streaming Infrastructure</b></summary>

- **High-Throughput Go Gateway**: Low-overhead HTTP/gRPC ingestion gateway built with Go 1.22.
- **Apache Kafka Event Broker**: Distributed transaction topic partitioning (`transactions.raw`) with IBM Sarama driver.
- **Redis Idempotency & Rate Limiting**: Deduplication of duplicate transaction IDs and per-IP rate throttling.
- **Circuit Breaker Pattern**: Resilient fallback handling when ML inference engine is under heavy load.
- **PostgreSQL Persistence**: Structured transaction logging, historical baselines, and prediction tracking.
</details>

<details open>
<summary><b>🖥️ Frontend Dashboard & DevOps</b></summary>

- **React 18 + Vite Dashboard**: High-performance dashboard built with TypeScript, React Query, and TailwindCSS.
- **Interactive Visualizations**: Recharts integration for real-time fraud trends, decision distribution pie charts, and KPI cards.
- **Code-Split Bundles**: Rollup manual chunking delivering a lightweight **31 KB** main bundle footprint.
- **Nginx Reverse Proxy**: Single entry point routing `/api/*` to Go Gateway and `/ml/*` to Python ML Engine with Gzip compression.
- **GitHub Actions CI/CD**: Automated linting, typechecking, unit tests, and Docker Compose validation on every push.
</details>

---

## 🔄 End-to-End Request Flow

```
 [ Client / Load Simulator ]
             │
             │ 1. POST /api/transactions
             ▼
  ┌──────────────────────┐
  │  Nginx Reverse Proxy │
  └──────────┬───────────┘
             │ 2. Proxy request
             ▼
  ┌──────────────────────┐      3. Deduplicate & Rate-Limit
  │  Go Ingestion Gateway│ ──────────────────────────────────▶ [ Redis Cache ]
  └──────────┬───────────┘
             │ 4. Publish Event (Async)
             ├───────────────────────────────────────────────▶ [ Apache Kafka ]
             │ 5. Save Raw Transaction
             ├───────────────────────────────────────────────▶ [ PostgreSQL DB ]
             │
             │ 6. Synchronous Risk Scoring (gRPC / REST)
             ▼
  ┌──────────────────────┐
  │ Python ML Engine     │ ──▶ [ XGBoost Model ] ──▶ Score: 0.91 (BLOCK)
  └──────────┬───────────┘
             │ 7. Return Prediction & Write Audit Log
             ▼
  ┌──────────────────────┐
  │  Go Ingestion Gateway│ ──▶ 8. Persist Prediction ──▶ [ PostgreSQL DB ]
  └──────────┬───────────┘
             │
             │ 9. Return Fraud Status & Response Payload
             ▼
 [ Client / React Dashboard ] ──▶ 10. Prometheus Scrape ──▶ [ Grafana ]
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Dashboard (Vite)                   │
│                    fraud-dashboard:3001                       │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               Nginx Reverse Proxy (:80)                      │
│           /api/ → ingestion-gateway:8080                     │
│           /ml/  → ml-anomaly-engine:8000                     │
└────────────┬─────────────────────────┬───────────────────────┘
             │                         │
             ▼                         ▼
┌────────────────────────┐  ┌──────────────────────────────────┐
│  Go Ingestion Gateway  │  │   Python ML Anomaly Engine       │
│   (REST + gRPC + Kafka)│  │   FastAPI + XGBoost + Registry   │
│   ingestion-gateway:   │  │   ml-anomaly-engine:8000         │
│   8080 (HTTP)          │  └────────────┬─────────────────────┘
│   50051 (gRPC)         │               │
└────────┬───────────────┘               │
         │                               │
         ▼                               ▼
┌────────────────┐              ┌─────────────────┐
│   PostgreSQL   │◄─────────────│   PostgreSQL    │
│   :5432        │              │   (shared DB)   │
└────────────────┘              └─────────────────┘
         │
         ▼
┌────────────────┐   ┌─────────────┐   ┌──────────────────┐
│     Redis      │   │    Kafka    │   │    Zookeeper     │
│  Rate Limiting │   │  Streaming  │   │  Kafka Coord.    │
│   :6379        │   │   :9092     │   │    :2181         │
└────────────────┘   └─────────────┘   └──────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Observability Stack             │
│  Prometheus (:9090) + Grafana (:3000)   │
└─────────────────────────────────────────┘
```

### Microservice Inventory

| Service | Container Name | Port | Description |
|---|---|---|---|
| **fraud-dashboard** | `fintech-dashboard` | `3001` | React + TypeScript Vite Operations Dashboard |
| **ingestion-gateway** | `fintech-ingestion-gateway` | `8080` (HTTP), `50051` (gRPC) | Go API Gateway, Kafka Producer, Redis Limiter |
| **ml-anomaly-engine** | `fintech-ml-engine` | `8000` | Python FastAPI Inference Engine & Model Registry |
| **transaction-simulator** | `fintech-simulator` | — | Go load generator producing realistic transaction mixes |
| **postgres** | `fintech-postgres` | `5432` | Primary PostgreSQL relational data store |
| **redis** | `fintech-redis` | `6379` | In-memory store for idempotency keys & rate limits |
| **kafka** | `fintech-kafka` | `9092` | Event streaming broker for transaction topics |
| **zookeeper** | `fintech-zookeeper` | `2181` | Cluster management and coordination for Kafka |
| **nginx** | `fintech-nginx` | `80` | Reverse proxy load balancing API routes |
| **prometheus** | `fintech-prometheus` | `9090` | Time-series metrics collection engine |
| **grafana** | `fintech-grafana` | `3000` | Analytics visualization and alerting UI |

---

## 💻 Tech Stack

| Category | Technologies & Frameworks |
|---|---|
| **Frontend** | ![React](https://img.shields.io/badge/React-18-61DAFB?logo=react) ![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript) ![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?logo=vite) ![Tailwind](https://img.shields.io/badge/Tailwind-4.0-06B6D4?logo=tailwindcss) React Query, Axios, Recharts |
| **Backend Gateway** | ![Go](https://img.shields.io/badge/Go-1.22-00ADD8?logo=go) net/http, gRPC, Protocol Buffers, IBM Sarama Kafka Driver, Go-Redis |
| **Machine Learning** | ![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi) XGBoost, scikit-learn, pandas, numpy, joblib, PyArrow |
| **Database & Cache** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql) ![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis) |
| **Event Streaming** | ![Kafka](https://img.shields.io/badge/Apache_Kafka-7.5-231F20?logo=apachekafka) Confluent Zookeeper 7.5 |
| **Observability** | ![Prometheus](https://img.shields.io/badge/Prometheus-Latest-E6522C?logo=prometheus) ![Grafana](https://img.shields.io/badge/Grafana-Latest-F46800?logo=grafana) |
| **Proxy & DevOps** | ![Nginx](https://img.shields.io/badge/Nginx-1.27-009639?logo=nginx) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker) GitHub Actions CI/CD |

---

## 📚 Documentation Hub

The table below outlines the comprehensive technical documentation available in the [`docs/`](docs/) directory:

| Guide | Description | Recommended Reading Context |
|---|---|---|
| [**Architecture**](docs/architecture.md) | Full architectural blueprint, service inventory, and network layout | Read first to understand system topology |
| [**System Design**](docs/system-design.md) | Component responsibilities, request lifecycles, and trade-offs | Read for deep-dive backend & design rationale |
| [**ML Pipeline**](docs/ml-pipeline.md) | IBM dataset feature engineering, model training, registry & drift | Read when working on ML models & retraining |
| [**API Reference**](docs/api.md) | Complete REST & gRPC endpoint documentation with request/response schemas | Read when building integrations or frontend features |
| [**Security Guide**](docs/security.md) | JWT authentication, RBAC policy, password hashing, and Docker security | Read before deploying to production |
| [**Deployment Guide**](docs/deployment.md) | Step-by-step production deployment for Vercel, Railway, Render & AWS | Read when preparing cloud deployments |
| [**Contributing**](CONTRIBUTING.md) | Local development setup, testing commands, and PR guidelines | Read before submitting contributions |

### 🗺️ Recommended Reading Order

```
  README.md (Project Overview)
      │
      ▼
  docs/architecture.md (System Blueprint)
      │
      ▼
  docs/system-design.md (Design Rationale & Trade-offs)
      │
      ├───────────────────────────────┐
      ▼                               ▼
  docs/ml-pipeline.md (ML Engine)   docs/api.md (API Contracts)
      │                               │
      └───────────────────────────────┤
                                      ▼
                             docs/security.md & docs/deployment.md
```

---

## ⚡ Quick Start

Follow these steps to spin up the entire multi-container platform locally.

### Prerequisites
- [Docker 24+](https://docs.docker.com/get-docker/) and Docker Compose v2
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/Vaibhav20k/fintech-pipeline.git
cd fintech-pipeline
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```
*(Optionally modify `.env` to customize default ports or secrets)*

### Step 3: Launch with Docker Compose
```bash
docker compose up -d --build
```

### Step 4: Verify Cluster Health
```bash
docker compose ps
```

### Step 5: Access Service Endpoints

| Endpoint | Target URL | Credentials / Notes |
|---|---|---|
| **Fraud Dashboard** | [http://localhost:3001](http://localhost:3001) | React Operations UI |
| **Nginx Reverse Proxy** | [http://localhost](http://localhost) | Main API Entry Point |
| **Go Gateway API** | [http://localhost:8080](http://localhost:8080) | REST & Health Probes |
| **Python ML Engine API** | [http://localhost:8000](http://localhost:8000) | OpenAPI / Swagger Docs at `/docs` |
| **Prometheus UI** | [http://localhost:9090](http://localhost:9090) | Telemetry Target Scraping |
| **Grafana UI** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` |

---

## 🗂️ Folder Structure

```
fintech-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD Pipeline
├── fraud-dashboard/               # React 18 + TypeScript + Vite Dashboard
│   ├── src/
│   │   ├── components/            # Reusable UI components & charts
│   │   ├── hooks/                 # React Query data-fetching hooks
│   │   ├── pages/                 # Dashboard views
│   │   ├── services/              # Axios API client
│   │   └── types/                 # TypeScript interfaces
│   ├── Dockerfile                 # Production multi-stage Nginx container
│   └── package.json
├── ingestion-gateway/             # Go 1.22 REST/gRPC API Gateway
│   ├── cmd/server/                # Gateway main entry point
│   ├── internal/
│   │   ├── api/handler/           # HTTP handlers (transactions, predictions)
│   │   ├── config/                # Environment configuration loader
│   │   ├── kafka/                 # Sarama Kafka producer/consumer
│   │   ├── middleware/            # Rate limiting, IP extraction, CORS
│   │   ├── ml/                    # ML client with Circuit Breaker
│   │   └── server/                # HTTP & gRPC server initializers
│   ├── proto/                     # Protocol Buffer definitions
│   └── Dockerfile                 # Multi-stage Go build container
├── ml-anomaly-engine/             # Python 3.11 FastAPI ML Engine
│   ├── auth/                      # JWT token handler & RBAC dependencies
│   ├── config/                    # Database & settings manager
│   ├── inference/                 # FastAPI routes, schemas, predictors
│   ├── models/                    # Model Registry JSON & saved PKLs
│   ├── monitoring/                # Population Stability Index (PSI) drift detector
│   ├── retraining/                # Automated model retraining pipeline
│   ├── services/                  # Audit logger & model manager
│   ├── tests/                     # Pytest suite
│   ├── Dockerfile                 # Lightweight Python runtime container
│   └── requirements.txt           # Pinned dependencies
├── transaction-simulator/         # Go transaction load generator
├── database/                      # PostgreSQL init scripts & migrations
├── nginx/                         # Reverse proxy configuration
├── observability/                 # Prometheus config & Grafana definitions
├── docs/                          # Comprehensive technical guides
├── docker-compose.yml             # Full-stack orchestrator
└── .env.example                   # Master environment template
```

---

## 🔐 Authentication & Security

The ML Engine implements strict JWT Bearer token authentication with Role-Based Access Control (RBAC).

### Development Credentials

> ⚠️ **Warning**: Default development credentials. Always update passwords in `.env` before production deployment.

| Username | Password | Role | Access Scope |
|---|---|---|---|
| `admin` | `admin123` | `admin` | Full read/write access + Model Registration & Activation |
| `analyst` | `analyst123` | `analyst` | Read-only access to predictions, stats, and drift metrics |

### Authenticating via API

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response Payload:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "admin"
}
```

Include the access token in subsequent request headers:
```http
Authorization: Bearer <access_token>
```

---

## 📡 API Reference Summary

Below is an overview of core API endpoints. See [`docs/api.md`](docs/api.md) for full request/response schemas.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/transactions` | None | Submit a transaction for ingestion and synchronous risk scoring |
| `GET` | `/api/predictions` | None | Retrieve historical predictions for dashboard viewing |
| `GET` | `/api/dashboard/summary` | None | Get KPI metrics (total count, fraud count, fraud rate) |
| `POST` | `/ml/predict` | Bearer | Synchronous ML fraud probability prediction |
| `GET` | `/ml/models` | Bearer | List all registered model versions |
| `GET` | `/ml/models/active` | Bearer | Retrieve active model details |
| `POST` | `/ml/models/activate` | Admin | Hot-swap active model version |
| `POST` | `/ml/models/register` | Admin | Register new trained model artifact |
| `GET` | `/ml/monitoring` | Bearer | Get live model inference statistics |
| `GET` | `/ml/drift` | Bearer | Run statistical drift detection (PSI) |
| `GET` | `/health` | None | Gateway liveness probe |

---

## 🤖 ML Pipeline & Performance

DualSentry utilizes an **XGBoost Classifier** optimized for tabular transaction evaluation.

### Model Metrics

| Metric | XGBoost v2 (Production) | Isolation Forest (Baseline) |
|---|---|---|
| **Accuracy** | **97.2%** | 85.1% |
| **Precision** | **91.4%** | 72.3% |
| **Recall** | **88.6%** | 81.0% |
| **F1-Score** | **0.899** | 0.764 |
| **AUC-ROC** | **0.982** | 0.912 |

### Feature Engineering
- **Temporal**: `hour`, `day_of_week`, `is_weekend` derived from ISO timestamps.
- **Account Ratios**: `amount_to_balance_ratio` (`amount / from_account_balance`).
- **State History**: Historical account transaction velocity maintained by Go `baseline_updater`.

---

## 📊 Observability & Monitoring

DualSentry provides end-to-end monitoring out of the box:

- **Prometheus Metrics**: Exported at `http://localhost:8080/metrics` and `http://localhost:8000/metrics`.
- **Latency Histogram**: Tracks `http_request_duration_seconds` for p50, p90, and p99 latency SLAs.
- **Request Counters**: Tracks `http_requests_total` by HTTP method, route, and status code.
- **Structured Audit Logging**: Predictions and admin actions logged with timestamp and user context to `logs/audit.log`.

---

## 🔄 CI/CD Pipeline

Automated quality control is executed on every GitHub push/PR via `.github/workflows/ci.yml`:

```
┌─────────────────────────────────────────────────────────────┐
│                 GitHub Actions CI/CD Pipeline               │
└─────┬──────────────┬──────────────┬──────────────┬──────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Go CI    │  │ Python CI │  │React Frontend│  │ Docker    │
│ • go fmt  │  │ • flake8  │  │ • tsc check│  │ • compose │
│ • go vet  │  │ • pytest  │  │ • eslint   │  │   syntax  │
│ • go test │  │   suite   │  │ • vite     │  │   check   │
│ • build   │  └───────────┘  │   build    │  └───────────┘
└───────────┘                 └───────────┘
```

---

## 🗺️ Product Roadmap

- [x] Multi-stage containerized microservices architecture
- [x] Zero-downtime model registry hot-swapping
- [x] Statistical drift detection (Population Stability Index)
- [x] Vite React frontend code-splitting (< 50KB main bundle)
- [ ] Real-time WebSocket alerts for high-risk fraud detections
- [ ] Grafana dashboard automated JSON provisioning
- [ ] Kubernetes Helm Chart for production deployments
- [ ] SHAP model explainability breakdown endpoint

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Review [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup and coding standards.
2. Fork the repository and create your feature branch: `git checkout -b feat/my-feature`.
3. Verify all test suites pass (`go test`, `pytest`, `tsc --noEmit`).
4. Commit your changes and open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
