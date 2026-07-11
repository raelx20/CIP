# Production Deployment Guide (Vercel + Supabase)

## Architecture

```
┌─────────────────────────────────────────────┐
│                  Vercel                      │
│  ┌──────────────┐     ┌──────────────────┐  │
│  │   Frontend   │     │    Backend       │  │
│  │   Next.js    │────▶│  FastAPI (Python)│  │
│  │  /frontend/* │     │  /api/*          │  │
│  └──────────────┘     └────────┬─────────┘  │
└────────────────────────────────┼────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
             ┌──────────────┐        ┌──────────────┐
             │   Supabase   │        │   Upstash    │
             │  (PostGIS)   │        │   (Redis)    │
             └──────────────┘        └──────────────┘
```

## Prerequisites

- GitHub account
- Vercel account (free)
- Supabase account (free tier)
- Upstash account (free tier)

## Step 1: Supabase (Database)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note the **Connection URI** from Settings → Database:
   ```
   postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
3. Enable PostGIS:
   - Go to SQL Editor
   - Run: `CREATE EXTENSION IF NOT EXISTS postgis;`

## Step 2: Upstash (Redis)

1. Go to [upstash.com](https://upstash.com) and create a Redis instance
2. Note the **Redis URL** from the console:
   ```
   redis://default:[password]@[endpoint]:6379
   ```

## Step 3: Vercel (Frontend + Backend)

1. Go to [vercel.com](https://vercel.com) and **Import Git Repository**
2. Select `raelx20/CIP`
3. Vercel will auto-detect the configuration from `vercel.json`
4. Add these **Environment Variables** in the Vercel dashboard:

   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | Your Supabase URI (change `postgresql://` to `postgresql+asyncpg://`) |
   | `REDIS_URL` | Your Upstash Redis URL |
   | `JWT_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
   | `ENVIRONMENT` | `production` |
   | `LLM_BASE_URL` | Your LLM endpoint (e.g., `https://api.openai.com/v1`) |
   | `LLM_API_KEY` | Your LLM API key |
   | `LLM_MODEL` | Your model name (e.g., `gpt-4o-mini`) |
   | `GOOGLE_MAPS_API_KEY` | Your Google Maps API key |

5. Deploy

## Step 4: Run Migrations

Migrations need to be run manually since Vercel serverless functions don't support Alembic CLI.

### Option A: Via Supabase SQL Editor
Go to SQL Editor and run the migration SQL from `backend/migrations/versions/`.

### Option B: Via a one-time script
```bash
# Clone the repo locally
git clone https://github.com/raelx20/CIP.git
cd CIP

# Create .env with your production DATABASE_URL
echo "DATABASE_URL=postgresql+asyncpg://..." > backend/.env
echo "JWT_SECRET_KEY=your-key" >> backend/.env

# Run migrations
cd backend
pip install -r requirements.txt
alembic upgrade head
```

## Step 5: Create Admin User

```bash
# Via Supabase SQL Editor
INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'admin@cip.gov',
  '$2b$12$LJ3m4ys3Lk0TSwMFQqGqjOQxKjQxKjQxKjQxKjQxKjQxKjQxKjQxKj',  -- bcrypt hash of 'Admin123!'
  'System Admin',
  'admin',
  true,
  NOW(),
  NOW()
);
```

Or use a Python script:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("Admin123!"))
```

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection (asyncpg) | `postgresql+asyncpg://user:pass@host:6543/db` |
| `JWT_SECRET_KEY` | Secret for JWT signing | `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `REDIS_URL` | Redis connection | `redis://default:pass@host:6379` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `production` for live |
| `DEBUG` | `false` | Enable debug mode |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | LLM API endpoint |
| `LLM_API_KEY` | `ollama` | LLM API key |
| `LLM_MODEL` | `qwen3:1.7b` | LLM model name |
| `GOOGLE_MAPS_API_KEY` | `""` | Google Maps API key |

## Your Production URLs

After deployment, your URLs will be:

| Service | URL |
|---------|-----|
| Frontend | `https://cip.vercel.app` |
| Backend API | `https://cip.vercel.app/api/v1/...` |
| API Docs | `https://cip.vercel.app/api/v1/system/health` |

## Troubleshooting

### Backend won't start
- Check Vercel function logs in the dashboard
- Verify `DATABASE_URL` uses `postgresql+asyncpg://` (not `postgresql://`)
- Verify `JWT_SECRET_KEY` is set

### Database connection refused
- Verify Supabase project is active
- Check if IP whitelist is enabled (disable for Vercel)
- Verify connection string format

### CORS errors
- In Vercel, the frontend and backend are on the same domain, so CORS shouldn't be an issue
- If you see CORS errors, check that `BACKEND_CORS_ORIGINS` includes your Vercel URL

### Cold starts
- First request to the backend may take 2-5 seconds
- Subsequent requests are fast
- This is normal for serverless Python functions
