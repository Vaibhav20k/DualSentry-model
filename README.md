# AI-Augmented Real-Time Financial Risk Intelligence Platform

> A research-oriented, distributed fraud detection system that replaces static rule-based thresholds with **adaptive behavioral baselines**, **streaming anomaly detection**, and **LLM-grounded explanations** — built to be evaluated, not just deployed.

[![Status](https://img.shields.io/badge/status-in%20development-orange)]()
[![Go](https://img.shields.io/badge/backend-Go-00ADD8?logo=go&logoColor=white)]()
[![Python](https://img.shields.io/badge/ML-Python-3776AB?logo=python&logoColor=white)]()
[![Kafka](https://img.shields.io/badge/streaming-Kafka-231F20?logo=apachekafka&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

---

## Overview

Traditional rule-based fraud systems fail against adaptive adversaries: fraudsters observe which patterns trigger alerts and shift their behavior just enough to stay under the threshold. This platform is built around a different premise — model each user's **behavioral baseline**, score deviations from it in a streaming pipeline, and pair every risk score with a **feature-grounded, natural-language explanation** so a human analyst can trust and act on it quickly.

This is a systems + research project, not just an application. A companion research paper covering the threat model, mathematical formulation, and evaluation plan is included in [`/docs/research-paper.pdf`](./docs).

**Read this before anything else:** this project is under active development. The table in [Project Status](#project-status) below is the source of truth for what's actually built versus what's designed but not yet implemented.

---

## Why This Exists

| Problem with static rule-based fraud systems | This platform's approach |
|---|---|
| Fixed thresholds don't adapt to evolving fraud patterns | Per-user behavioral baselines that adapt over time |
| Binary "flagged / not flagged" gives analysts no context | Every score ships with a feature-grounded explanation |
| Static systems are naive to adversaries who slowly shift behavior | A drift-plausibility check guards baseline adaptation against slow poisoning |
| "Risk = 0.91" tells an analyst nothing actionable | "Flagged: amount exceeds 99th percentile, unseen device, new merchant, impossible travel" |

---

## Architecture

```
                     ┌──────────────┐
                     │    Client    │
                     └──────┬───────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Go gRPC Ingestion    │
                │       Gateway         │
                └───────────┬───────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     Kafka     │
                    │ Event Stream  │
                    └───────┬───────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Feature Engineering    │
              │ (behavioral baseline     │
              │   lookup + update)       │
              └────────────┬─────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  ML Anomaly Detection    │
              │   (risk score R)         │
              └────────────┬─────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   LLM Explanation Layer  │
              │  (grounded in R's        │
              │   feature attributions)  │
              └────────────┬─────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    └───────┬───────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  Dashboard + Monitoring  │
              │  (Prometheus / Grafana)  │
              └─────────────────────────┘
```

The scoring model (ML) and the explanation model (LLM) are deliberately decoupled: the LLM never sees raw account data, only the already-computed feature deltas that produced the score. This is intended to keep explanations **faithful** to the actual decision, not just plausible-sounding.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion API | Go, gRPC, Protocol Buffers |
| Event Streaming | Apache Kafka |
| Feature Store / Database | PostgreSQL, Redis |
| ML — Anomaly Detection | Python, scikit-learn (Isolation Forest / statistical baselines) |
| Explanation Layer | LLM-based explanation generation |
| Observability | Prometheus, Grafana |
| Infrastructure | Docker, Docker Compose |

---

## Behavioral Baseline Model

Each user `u` is represented by a running behavioral baseline rather than a static rule set:

```
Bᵤ = { μₐ, σₐ, H, M, L, τ }
```

- `μₐ, σₐ` — running mean/stddev of transaction amount
- `H` — historical distribution of transaction hours
- `M` — previously seen merchants
- `L` — previously seen device/location fingerprints
- `τ` — drift-adaptation rate

A transaction `x` is scored as `R = f(x, Bᵤ)`, and explained as `E = g(x, R, Bᵤ)` — the explanation function is constrained to use the same feature attributions that produced the score.

Full derivation, threat model, and research questions are in the [research paper](./docs).

---

## Project Status

This project is being built incrementally. Status is tracked honestly here rather than implied by feature lists — items marked **Planned** do not exist in the codebase yet.

| Component | Status |
|---|---|
| Docker infrastructure (Postgres, Redis, Kafka) | ✅ Complete |
| Database schema (`transactions`, `user_baselines`, `anomaly_logs`) | ✅ Complete |
| gRPC API contract + generated protobuf | ✅ Complete |
| Go module, config, logging, server bootstrap | ✅ Complete |
| Transaction persistence | 🔲 Planned |
| Kafka producer / streaming ingestion | 🔲 Planned |
| ML anomaly detection engine | 🔲 Planned |
| LLM explanation engine | 🔲 Planned |
| Evaluation on labeled data | 🔲 Planned |
| Dashboard / monitoring | 🔲 Planned |
| CI/CD | 🔲 Planned |

---

## Database Schema (current)

```
transactions      — raw transaction events
user_baselines     — per-user behavioral baseline state (Bᵤ)
anomaly_logs        — scored transactions + explanation output
```

---

## Getting Started

```bash
git clone https://github.com/Vaibhav20k/<repo-name>.git
cd <repo-name>

# Start infrastructure
docker-compose up -d

# Run the Go ingestion gateway
go run ./cmd/gateway
```

> ⚠️ The pipeline is not end-to-end functional yet — see [Project Status](#project-status). Infrastructure and the ingestion gateway boot successfully; scoring and explanation stages are not yet wired in.

### Requirements

- Go 1.22+
- Python 3.10+
- Docker & Docker Compose
- Apache Kafka (via Docker Compose)
- PostgreSQL 15+

---

## Evaluation Metrics (planned)

Once the ML and explanation components are implemented, the system will be evaluated on:

- **Detection quality:** ROC-AUC, Precision, Recall, F1 (time-ordered holdout split)
- **System performance:** end-to-end latency, throughput, Kafka consumer lag, resource utilization
- **Robustness:** performance under a simulated slow-drift adversary (see research paper, RQ4)

---

## Research Questions

1. Do per-user behavioral baselines reduce false positives relative to static, population-level thresholds at matched recall?
2. Do LLM-generated, feature-grounded explanations measurably improve analyst response, and are they faithful to the model's actual feature attributions?
3. Can the full streaming pipeline sustain sub-100ms end-to-end latency at realistic transaction throughput?
4. Do adaptive baselines with a poisoning-aware drift check outperform static thresholds *and* naive (unguarded) adaptive baselines under a simulated slow-drift adversary?

---

## Threat Model (summary)

The system is designed against adversaries who don't just try to evade a single check, but try to shift what the system considers "normal" over time:

- Account takeover
- Synthetic identity fraud
- Mule accounts / laundering networks
- Slow adversarial drift (gradual behavior shift to stay inside an adapting baseline)
- Poisoning of the drift-adaptation mechanism itself

Full threat model in the [research paper](./docs).

---

## Roadmap

- [ ] Transaction persistence + Kafka producer
- [ ] Baseline anomaly detector (Isolation Forest / statistical z-score)
- [ ] LLM explanation layer with feature-faithfulness check
- [ ] Evaluation on public dataset (RQ1)
- [ ] Slow-drift adversary simulation (RQ4)
- [ ] Dashboard + monitoring
- [ ] CI/CD
- [ ] Graph-level detection for mule-account networks
- [ ] Continual/online learning under delayed labels

---

## Documentation

- [`/docs/research-paper.pdf`](./docs) — full research paper: motivation, related work, threat model, mathematical formulation, evaluation plan
- [`/docs/architecture.md`](./docs) — detailed system design *(add if/when written)*

---

## Contributing

This is currently a solo research/portfolio project. Issues and suggestions are welcome; PRs may be considered once the core pipeline is functional.

---

## License

MIT License

---

## Author

**Vaibhav Kandpal**
B.Tech Computer Science, Dr. Akhilesh Das Gupta Institute of Professional Studies (GGSIPU), Delhi
[GitHub](https://github.com/Vaibhav20k)# AI-Augmented Real-Time Financial Risk Intelligence Platform
B.Tech Computer Science, Dr. Akhilesh Das Gupta Institute of Professional Studies (GGSIPU), Delhi
[GitHub](https://github.com/Vaibhav20k)
