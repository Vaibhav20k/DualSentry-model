# System Architecture

This document describes the end-to-end architecture of the AI-Augmented Real-Time Financial Risk Intelligence Platform. It expands on the high-level diagram in the [README](../README.md) and explains the reasoning behind each design decision.

**Status note:** this document describes the target architecture. See the [Project Status table](../README.md#project-status) for what is currently implemented versus planned.

---

## Diagram

```
                              Client
                                │
                                ▼
                    Go gRPC Ingestion Gateway
                                │
                                ▼
                          Apache Kafka
                                │
            ┌───────────────────┴───────────────────┐
            │                                        │
            ▼                                        ▼
    User Baseline Store                     Feature Engineering
  (PostgreSQL + Redis)                                │
            │                                         │
            └──────────────┬──────────────────────────┘
                            ▼
                    ML Inference Engine
          (Isolation Forest / XGBoost / etc.)
                            │
            ┌───────────────┴───────────────┐
            ▼                                ▼
       Risk Score                  Feature Attribution
            │                                │
            └───────────────┬────────────────┘
                             ▼
                   LLM Explanation Engine
                             │
            ┌────────────────┴────────────────┐
            ▼                                  ▼
       PostgreSQL                        Prometheus
            │                                  │
            ▼                                  ▼
        Dashboard                          Grafana
```

---

## Component Breakdown

### 1. Client

Any upstream system emitting transaction events — a payment processor, a banking core, or a simulated event generator during development/evaluation. The client is intentionally decoupled from the platform: it only needs to speak the gRPC contract defined in the ingestion gateway's `.proto` files.

### 2. Go gRPC Ingestion Gateway

The single entry point into the platform. Written in Go for low-latency, high-throughput ingestion.

Responsibilities:
- Validates incoming transaction events against the protobuf schema
- Performs lightweight synchronous checks (auth, malformed payloads) before anything touches the pipeline
- Publishes valid events onto Kafka and returns immediately — the gateway does not block on scoring

This separation means ingestion throughput is not coupled to inference latency; if the ML or LLM stages slow down, the gateway keeps accepting traffic and Kafka absorbs the backlog.

### 3. Apache Kafka

The backbone of the pipeline. Decouples ingestion from processing and allows each downstream stage to consume at its own pace, replay events for debugging/evaluation, and scale independently.

Every transaction event flows through a single topic (or a small set of partitioned topics, keyed by user ID to preserve per-user ordering — see [Design Rationale](#per-user-ordering)).

From Kafka, the event fans out to two parallel consumers:

### 4a. User Baseline Store (PostgreSQL + Redis)

Maintains the behavioral baseline `Bᵤ = { μₐ, σₐ, H, M, L, τ }` for every user (see the [research paper](./research-paper.pdf) for the full formulation).

- **PostgreSQL** is the durable source of truth for baseline state
- **Redis** caches hot baselines in memory for low-latency reads during scoring, avoiding a Postgres round-trip on every transaction

Baseline updates are not applied unconditionally — a candidate update only lands if it passes a drift-plausibility check, which exists specifically to prevent an adversary from slowly poisoning a user's baseline (see the threat model in the research paper, particularly the slow-drift and poisoning adversary classes).

### 4b. Feature Engineering

Runs in parallel with the baseline lookup. Computes the actual feature vector for the incoming transaction:

- Deviation of transaction amount from `μₐ, σₐ`
- Whether the transaction hour falls outside the user's historical distribution `H`
- Whether the merchant is new (not in `M`)
- Whether the device/location fingerprint is new (not in `L`)
- Velocity features (e.g. transactions in the last N minutes)

The baseline lookup and feature engineering stages converge before scoring, since the feature vector is computed *against* the baseline, not independently of it.

### 5. ML Inference Engine

Consumes the merged baseline + feature vector and produces two outputs from a single forward pass:

- **Risk Score (`R`)** — the scalar anomaly score, `R = f(x, Bᵤ)`
- **Feature Attribution** — which specific features contributed most to `R` (e.g. via SHAP values, or native feature importances for tree-based models)

Candidate models: Isolation Forest (unsupervised, good for the cold-start/no-label case) or XGBoost (supervised, once labeled fraud data is available). The architecture is model-agnostic at this stage — the contract downstream only requires a risk score plus an attribution vector, not a specific model family.

**Why attribution is a first-class output, not an afterthought:** the LLM explanation stage is only allowed to explain what the model actually used. Producing attribution alongside the score — rather than deriving it separately, post-hoc — is what keeps the explanation faithful. See [Design Rationale](#faithful-vs-plausible-explanation).

### 6. LLM Explanation Engine

Takes the risk score and its feature attribution and produces `E = g(x, R, Bᵤ)` — a natural-language rationale grounded strictly in the attributed features.

Critically, the LLM does **not** receive the raw transaction or raw account history — only the already-computed score and attribution. This is a deliberate architectural constraint, not an implementation detail: it removes the LLM's ability to invent a plausible-sounding rationale that doesn't correspond to what the ML model actually flagged.

Output example:
> "Flagged: transaction amount exceeds the user's 99th percentile, device fingerprint not previously seen, merchant category new for this user."

### 7. PostgreSQL (results)

Final scored transactions, feature attributions, and generated explanations are persisted for analyst review, audit, and offline evaluation (see the Evaluation Plan in the research paper). This is a separate write path from the User Baseline Store, though it may live in the same database instance.

### 8. Prometheus

Collects operational telemetry from every stage of the pipeline: ingestion throughput, Kafka consumer lag, inference latency, explanation-generation latency, error rates. This is system-health telemetry, distinct from model-quality metrics (ROC-AUC, precision/recall), which are computed offline against the PostgreSQL results table.

### 9. Dashboard

Analyst-facing view: scored transactions, explanations, and case status. Reads from PostgreSQL.

### 10. Grafana

Operations-facing view: latency, throughput, error rates, resource utilization. Reads from Prometheus.

---

## Design Rationale

### Decoupling ingestion from processing

The gateway writes to Kafka and returns immediately rather than waiting for a score. This means ingestion-side latency is bounded and predictable even if the ML or LLM stages are under load or temporarily degraded — a requirement for any system handling live transaction traffic, where the gateway cannot become the bottleneck.

### Per-user ordering

Kafka partitioning is keyed by user ID so that events for a single user are processed in order. This matters specifically because the baseline `Bᵤ` is stateful and sequential — processing two transactions for the same user out of order could cause a baseline update to be computed against a state that hasn't caught up yet, corrupting the drift-adaptation logic described in the research paper.

### Why baseline lookup and feature engineering run in parallel

Both stages need the same event but produce independent outputs (current baseline state vs. computed feature deltas) that are only combined at scoring time. Running them in parallel rather than sequentially reduces per-transaction latency, which matters for the sub-100ms latency target (RQ3 in the research paper).

### Faithful vs. plausible explanation

This is the single most important architectural constraint in the system. An LLM given a raw transaction and asked "why might this be fraud?" will produce a fluent, plausible-sounding answer regardless of whether that answer reflects the actual reason the ML model flagged it. By forcing the LLM to consume only the model's own feature attribution — rather than reasoning independently over raw data — the explanation is constrained to be a translation of the model's actual decision, not a parallel, disconnected guess. This has not yet been empirically verified (see Limitations in the research paper) but is the reason the pipeline is structured with explicit attribution as an output of the ML stage rather than an input to a separate LLM reasoning step.

### Separating result storage from baseline storage

Baseline state (`User Baseline Store`) and scored-transaction results (`PostgreSQL` at the end of the pipeline) are logically separate concerns even if they share infrastructure. Baseline state is mutable, per-user, and read-heavy during scoring. Results are append-only and read-heavy during analyst review and offline evaluation. Keeping them logically separate avoids one workload's access patterns degrading the other's.

### Why Redis sits in front of the baseline store

Every transaction requires a baseline read before it can be scored. At production transaction volumes, a Postgres round-trip on the hot path for every single event is the most likely latency bottleneck in the whole pipeline. Redis caching of active baselines is what makes the sub-100ms latency target (RQ3) plausible at all.

---

## Open Design Questions

These are not yet resolved and are tracked here rather than presented as settled:

- **Drift-plausibility check algorithm.** The architecture assumes baseline updates pass some robustness check before being applied, but the specific algorithm (e.g. a trainable drift detector vs. a simpler statistical bound) has not been chosen. See RQ4 in the research paper.
- **Cold-start handling.** New users have no baseline. The current architecture doesn't yet specify a fallback scoring strategy (e.g. population-level baseline until enough history accumulates) for this case.
- **Attribution method for the ML stage.** SHAP is the likely default for tree-based models but adds computational overhead; whether it fits within the latency budget alongside everything else in the hot path is untested.
- **Explanation faithfulness verification.** No automated check yet exists to confirm the LLM's output actually reflects the attribution it was given, rather than drifting into generic language under certain inputs.

---

## Related Documents

- [`README.md`](../README.md) — project overview, tech stack, current status
- [`research-paper.pdf`](./research-paper.pdf) — full mathematical formulation, threat model, and evaluation plan