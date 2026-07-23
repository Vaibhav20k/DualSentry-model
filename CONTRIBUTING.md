# Contributing

Thank you for your interest in contributing to fintech-pipeline!

## Development Setup

### Full Stack (Docker)
```bash
cp .env.example .env
docker compose up -d
```

### Frontend (local dev)
```bash
cd fraud-dashboard
npm install
npm run dev
```

### Go Gateway (local dev)
```bash
cd ingestion-gateway
go mod download
go run ./cmd/server
```

### Python ML Engine (local dev)
```bash
cd ml-anomaly-engine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn inference.app:app --reload --port 8000
```

## Running Tests

```bash
# Go
cd ingestion-gateway && go test ./...

# Python
cd ml-anomaly-engine && pytest

# Frontend
cd fraud-dashboard && npm run lint && npx tsc --noEmit
```

## Pull Request Guidelines

1. Fork and create a feature branch: `feat/your-feature`
2. Make minimal, focused changes
3. Ensure all CI checks pass
4. Write or update tests for new functionality
5. Do not change the API contract without prior discussion

## Code Style

- **Go**: `gofmt` standard (enforced by CI)
- **Python**: `flake8` compliant
- **TypeScript**: ESLint + strict mode
