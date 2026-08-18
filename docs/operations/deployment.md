# 🚢 Deployment Guide

## Overview

This guide covers deploying the fintech-pipeline platform in production environments.

---

## Prerequisites

- Docker 24+ and Docker Compose v2
- A domain name (for SSL)
- At least 4GB RAM on the host

---

## 1. Environment Configuration

Copy and configure `.env.example`:

```bash
cp .env.example .env
```

**Critical settings for production:**

```env
ENVIRONMENT=production

# Generate a strong random secret:
# python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=<your-strong-random-secret>

POSTGRES_PASSWORD=<strong-db-password>
GF_SECURITY_ADMIN_PASSWORD=<strong-grafana-password>

# Set to your actual frontend domain
CORS_ALLOWED_ORIGIN=https://your-frontend-domain.com
```

> ⚠️ **Never commit `.env` files to version control.**

---

## 2. Docker Compose Production Start

```bash
docker compose up -d --build
```

Check all services are healthy:
```bash
docker compose ps
docker compose logs -f
```

---

## 3. Frontend Deployment (Vercel / Netlify)

The React frontend can be deployed as a static site:

```bash
cd fraud-dashboard
npm run build
# Upload ./dist to Vercel / Netlify / S3
```

**Vercel one-click deploy:**
1. Import the repository in Vercel
2. Set root directory to `fraud-dashboard`
3. Set environment variable:
   - `VITE_API_BASE_URL=https://your-backend-domain.com`

---

## 4. Backend Deployment Options

### Option A: Docker Host (DigitalOcean, Linode, Hetzner)

1. Copy the repository to your server
2. Configure `.env` with production values
3. Run `docker compose up -d --build`
4. Configure firewall to expose only ports 80 and 443

### Option B: Railway

1. Create a new project in Railway
2. Add services from Dockerfile for each service
3. Configure environment variables via Railway dashboard
4. Set up a PostgreSQL add-on and Redis add-on

### Option C: Render

1. Create a new Web Service from the repository
2. Point to `ingestion-gateway/Dockerfile` for the Go service
3. Point to `ml-anomaly-engine/Dockerfile` for the Python service
4. Add managed PostgreSQL and Redis instances

---

## 5. SSL / TLS (Production)

For production, terminate SSL at Nginx using Let's Encrypt.

Add to `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... proxy locations ...
}
```

Or use an external load balancer (Cloudflare, AWS ALB) for TLS termination.

---

## 6. Database Initialization

The PostgreSQL database is initialized automatically via:
```
database/init-db.sql
```

For migrations, apply files in `database/migrations/` in order.

---

## 7. Health Check Endpoints

Use these for load balancer health probes:

| Service | Health URL |
|---|---|
| Ingestion Gateway | `GET http://ingestion-gateway:8080/health` |
| ML Engine | `GET http://ml-anomaly-engine:8000/health` |

---

## 8. Production Checklist

- [ ] `JWT_SECRET_KEY` changed to a strong random value
- [ ] `POSTGRES_PASSWORD` changed
- [ ] `GF_SECURITY_ADMIN_PASSWORD` changed
- [ ] `CORS_ALLOWED_ORIGIN` set to actual frontend domain
- [ ] Firewall rules: only ports 80/443 public
- [ ] SSL/TLS configured
- [ ] Logs aggregation configured (e.g. Loki, CloudWatch)
- [ ] Backups configured for PostgreSQL `postgres_data` volume
- [ ] Monitoring alerts set up in Grafana
