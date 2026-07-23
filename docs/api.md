# 📡 API Reference

## Base URLs

| Service | Base URL |
|---|---|
| Ingestion Gateway (via Nginx) | `http://localhost/api` |
| Ingestion Gateway (direct) | `http://localhost:8080/api` |
| ML Anomaly Engine (via Nginx) | `http://localhost/ml` |
| ML Anomaly Engine (direct) | `http://localhost:8000` |

---

## Authentication

The ML Anomaly Engine uses **JWT Bearer token** authentication.

To obtain a token, call the `/login` endpoint (form-encoded, not JSON):

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "role": "admin"
}
```

Use the token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Ingestion Gateway Endpoints

### `GET /health`
Liveness probe.

**Response:**
```json
{ "status": "alive" }
```

### `GET /health/live`
Kubernetes liveness probe.

**Response:**
```json
{ "status": "alive" }
```

### `GET /health/ready`
Readiness probe.

**Response:**
```json
{ "status": "ready" }
```

### `GET /metrics`
Prometheus metrics endpoint.

---

### `POST /api/transactions`
Submit a transaction for processing and fraud scoring.

**Request Body:**
```json
{
  "transaction_id": "txn_unique_id",
  "amount": 1500.00,
  "from_account": "ACC001",
  "to_account": "ACC002",
  "payment_type": "TRANSFER",
  "payment_channel": "online",
  "timestamp": "2025-01-01T14:30:00Z"
}
```

**Response `200`:**
```json
{
  "transaction_id": "txn_unique_id",
  "status": "accepted",
  "fraud_score": 0.83,
  "is_fraud": true
}
```

---

### `GET /api/predictions`
Retrieve all fraud predictions from the database.

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "transaction_id": "txn_001",
    "fraud_score": 0.83,
    "is_fraud": true,
    "model_name": "xgboost_v2",
    "created_at": "2025-01-01T14:30:01Z"
  }
]
```

---

### `GET /api/dashboard/summary`
Retrieve KPI summary for the dashboard.

**Response `200`:**
```json
{
  "total_transactions": 15420,
  "fraud_count": 312,
  "fraud_rate": 0.0202,
  "avg_fraud_score": 0.71
}
```

---

### `GET /api/dashboard/trend`
Retrieve daily fraud trend data.

**Response `200`:**
```json
[
  { "date": "2025-01-01", "fraud_count": 14, "total_count": 820 }
]
```

---

## ML Anomaly Engine Endpoints

### `GET /health`
Basic health check.

**Response `200`:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "2.0",
  "active_model": "xgboost_v2"
}
```

### `GET /health/live`
Liveness probe.

### `GET /health/ready`
Readiness probe — confirms model is loaded.

---

### `POST /predict`
Run a fraud prediction. **Requires Bearer token.**

**Request Body:**
```json
{
  "transaction_id": "txn_001",
  "amount": 5000.00,
  "payment_type": "TRANSFER",
  "payment_channel": "online",
  "from_account": "ACC001",
  "to_account": "ACC002",
  "hour": 2,
  "day_of_week": 6,
  "is_weekend": 1,
  "account_age_days": 30,
  "from_account_balance": 5200.00,
  "to_account_balance": 100.00,
  "amount_to_balance_ratio": 0.96
}
```

**Response `200`:**
```json
{
  "transaction_id": "txn_001",
  "is_fraud": true,
  "fraud_probability": 0.91,
  "fraud_score": 0.91,
  "model_id": "xgboost_v2",
  "model_version": "2.0",
  "explanation": { ... }
}
```

---

### `GET /models`
List all registered models. **Requires Bearer token.**

**Response `200`:**
```json
{
  "active_model": "xgboost_v2",
  "models": [
    {
      "model_id": "xgboost_v2",
      "version": "2.0",
      "status": "ACTIVE",
      "accuracy": 0.97,
      "precision": 0.91,
      "recall": 0.88,
      "f1_score": 0.89
    }
  ]
}
```

---

### `GET /models/active`
Get the currently active model. **Requires Bearer token.**

---

### `GET /models/{model_id}`
Get a specific model by ID. **Requires Bearer token.**

---

### `POST /models/activate`
Switch the active model. **Requires Admin role.**

**Request Body:**
```json
{ "model_id": "xgboost_v1" }
```

---

### `POST /models/register`
Register a new model in the registry. **Requires Admin role.**

**Request Body:**
```json
{
  "model_id": "xgboost_v3",
  "version": "3.0",
  "model_type": "XGBoost",
  "model_path": "models/saved_models_v2/xgboost_v3.pkl",
  "accuracy": 0.98,
  "precision": 0.93,
  "recall": 0.91,
  "f1_score": 0.92,
  "description": "Retrained with extended dataset"
}
```

---

### `GET /monitoring`
Get live model monitoring statistics. **Requires Bearer token.**

---

### `GET /drift`
Get drift detection statistics. **Requires Bearer token.**

---

## Error Responses

| Status Code | Meaning |
|---|---|
| `400` | Bad Request — invalid input or feature validation error |
| `401` | Unauthorized — missing or invalid JWT token |
| `403` | Forbidden — insufficient role (requires Admin) |
| `404` | Not Found — model or resource not found |
| `409` | Conflict — model ID already exists |
| `500` | Internal Server Error |
