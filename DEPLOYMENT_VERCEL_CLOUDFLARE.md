# Multi-Cloud Production Deployment Guide: Vercel + Cloudflare

This guide covers deploying the **Constituency Intelligence Platform (CIP)** across a hybrid multi-cloud architecture leveraging **Vercel** for Next.js SSR & Python FastAPI Serverless Functions, and **Cloudflare** for DNS, Edge Proxying, Web Application Firewall (WAF), and Edge Health routing.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                              USER / CITIZEN                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 Cloudflare Edge Gateway (wrangler.toml)                │
│  • Edge Health & Caching          • Bot Protection & WAF (DDoS)        │
│  • Edge CORS Preflight Handling   • Smart Placement Across Regions      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Proxy (Origin Host)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                              Vercel Origin                             │
│  ┌─────────────────────────────┐      ┌─────────────────────────────┐  │
│  │    Next.js 16 Frontend      │      │    FastAPI Serverless API   │  │
│  │    (frontend/package.json)  │      │    (api/index.py -> app)    │  │
│  │    /.*                      │      │    /api/v1/*                │  │
│  └─────────────────────────────┘      └──────────────┬──────────────┘  │
└──────────────────────────────────────────────────────┼─────────────────┘
                                                       │ Async Engine
                         ┌─────────────────────────────┴────────────┐
                         ▼                                          ▼
             ┌──────────────────────┐                   ┌──────────────────────┐
             │       Supabase       │                   │       Upstash        │
             │  PostgreSQL + PostGIS│                   │     Redis Cache      │
             └──────────────────────┘                   └──────────────────────┘
```

---

## Prerequisites & External Services

1. **GitHub Repository**: Connected to your Vercel Project.
2. **Supabase Database (PostgreSQL + PostGIS)**:
   * Create database at [supabase.com](https://supabase.com).
   * Run `CREATE EXTENSION IF NOT EXISTS postgis;` in SQL Editor.
   * Note connection string: `postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:6543/postgres`.
3. **Upstash Redis**:
   * Create Redis instance at [upstash.com](https://upstash.com).
   * Note connection string: `redis://default:[PASSWORD]@[HOST]:6379`.

---

## Step 1: Deploying to Vercel

### 1.1 Vercel Project Setup
1. Import your Git repository into **Vercel** (`vercel.com`).
2. Vercel will auto-detect configuration from `vercel.json`:
   * **Python Serverless Builder**: `@vercel/python` building `api/index.py`.
   * **Next.js Frontend Builder**: `@vercel/next` building `frontend/package.json`.

### 1.2 Configure Environment Variables in Vercel
In Vercel Dashboard → Settings → Environment Variables, add:

| Variable Name | Description / Value Example |
| :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:6543/postgres` |
| `REDIS_URL` | `redis://default:[PASSWORD]@[HOST]:6379` |
| `JWT_SECRET_KEY` | Generate via: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `ENVIRONMENT` | `production` |
| `LLM_BASE_URL` | Your OpenAI or cloud LLM endpoint (`https://api.openai.com/v1`) |
| `LLM_API_KEY` | Your LLM API key |
| `LLM_MODEL` | `gpt-4o-mini` (or your chosen model) |
| `GOOGLE_MAPS_API_KEY` | Your Google Maps Geocoding API key |

### 1.3 Trigger Vercel Build & Run Migrations
Deploy the Vercel project (`vercel --prod`). Once deployed, run database migrations against your live database using your local terminal:
```powershell
# Set production sync connection URL locally and run Alembic
$env:DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST]:6543/postgres"
cd backend
alembic upgrade head
```

---

## Step 2: Deploying Cloudflare Edge Gateway

The repository includes a production Cloudflare Workers configuration (`wrangler.toml` and `scripts/cloudflare/edge_proxy.js`) to front your Vercel deployment with edge caching, security headers, and instant health checks.

### 2.1 Install Wrangler CLI & Login
```powershell
npm install -g wrangler
wrangler login
```

### 2.2 Configure Origin Backend URL
In `wrangler.toml`, ensure `ORIGIN_BACKEND_URL` matches your deployed Vercel domain:
```toml
[vars]
ENVIRONMENT = "production"
ORIGIN_BACKEND_URL = "https://cip-yourproject.vercel.app"
```

### 2.3 Deploy Cloudflare Edge Worker
Deploy your Edge Gateway directly using Cloudflare Wrangler:
```powershell
wrangler deploy --env production
```

### 2.4 Custom Domain & DNS Setup (Cloudflare Dashboard)
1. In Cloudflare Dashboard → **DNS**, add a CNAME record pointing your domain (`cip.yourdomain.gov`) to your Cloudflare Worker / Vercel origin.
2. In **SSL/TLS**, set encryption mode to **Full (strict)**.
3. In **Workers & Pages → Routes**, bind your custom domain pattern:
   * Route Pattern: `cip.yourdomain.gov/*`
   * Worker: `cip-edge-gateway-prod`

---

## Verification & Health Check Endpoints

Once deployed across Vercel and Cloudflare, verify endpoints from your terminal or browser:

1. **Cloudflare Edge Health Check (Zero-Origin Roundtrip)**:
   ```bash
   curl https://cip.yourdomain.gov/cdn-cgi/edge-health
   # Returns: {"status":"healthy","layer":"Cloudflare Edge Gateway", ...}
   ```

2. **Vercel FastAPI Backend Health & Readiness**:
   ```bash
   curl https://cip.yourdomain.gov/api/v1/system/health
   # Returns: {"status":"healthy","service":"Constituency Intelligence Platform","version":"1.0.0"}
   
   curl https://cip.yourdomain.gov/api/v1/system/ready
   # Returns status of PostgreSQL and Redis connections
   ```
