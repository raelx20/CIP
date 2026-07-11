# Production Deployment Guide

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Vercel    │────▶│   Railway    │────▶│   Supabase   │
│  (Frontend) │     │  (Backend)   │     │  (Database)  │
│  Next.js    │     │  FastAPI     │     │  PostGIS     │
└─────────────┘     └──────────────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Upstash    │
                    │   (Redis)    │
                    └──────────────┘
```

## Prerequisites

- GitHub account
- Vercel account (free)
- Railway account (free tier)
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
4. Note the **Service Role Key** from Settings → API (for admin operations)

## Step 2: Upstash (Redis)

1. Go to [upstash.com](https://upstash.com) and create a Redis instance
2. Note the **Redis URL** from the console:
   ```
   redis://default:[password]@[endpoint]:6379
   ```

## Step 3: Railway (Backend)

1. Go to [railway.app](https://railway.app) and create a new project
2. Connect your GitHub repository
3. Set the **root directory** to `backend`
4. Add these environment variables:

   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | Your Supabase connection URI (change `postgresql://` to `postgresql+asyncpg://`) |
   | `REDIS_URL` | Your Upstash Redis URL |
   | `JWT_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
   | `ENVIRONMENT` | `production` |
   | `DEBUG` | `false` |
   | `BACKEND_CORS_ORIGINS` | `["https://your-app.vercel.app"]` |
   | `LLM_BASE_URL` | Your LLM endpoint (e.g., OpenAI API URL) |
   | `LLM_API_KEY` | Your LLM API key |
   | `LLM_MODEL` | Your model name |
   | `GOOGLE_MAPS_API_KEY` | Your Google Maps API key |

5. Railway will auto-deploy from the `railway.json` config
6. Note the **public URL** (e.g., `https://backend-production-xxxx.up.railway.app`)

## Step 4: Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com) and import your GitHub repository
2. Set the **root directory** to `frontend`
3. Add environment variable:

   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | Your Railway backend URL (e.g., `https://backend-production-xxxx.up.railway.app`) |

4. Deploy

## Step 5: Update CORS

After getting your Vercel URL, update the Railway backend environment:

```
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
```

## Step 6: Run Migrations

Railway runs `alembic upgrade head` on deploy. If you need to run manually:

```bash
# Via Railway CLI
railway run alembic upgrade head

# Or via Supabase SQL Editor, run the migration SQL manually
```

## Step 7: Create Admin User

```bash
# Via Railway CLI
railway run python -c "
from app.security.authentication import hash_password
from app.infrastructure.database.repositories.user import UserRepository
from app.database.session import AsyncSessionLocal
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.create({
            'email': 'admin@cip.gov',
            'hashed_password': hash_password('Admin123!'),
            'full_name': 'System Admin',
            'role': 'admin',
            'is_active': True,
        })
        print(f'Admin user created: {user.id}')

asyncio.run(create_admin())
"
```

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection (asyncpg) | `postgresql+asyncpg://user:pass@host:6543/db` |
| `JWT_SECRET_KEY` | Secret for JWT signing | `openssl rand -base64 64` |
| `REDIS_URL` | Redis connection | `redis://default:pass@host:6379` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `production` for live |
| `DEBUG` | `false` | Enable debug mode |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed origins |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | LLM API endpoint |
| `LLM_API_KEY` | `ollama` | LLM API key |
| `LLM_MODEL` | `qwen3:1.7b` | LLM model name |
| `GOOGLE_MAPS_API_KEY` | `""` | Google Maps API key |

## Troubleshooting

### Backend won't start
- Check Railway logs: `railway logs`
- Verify `DATABASE_URL` uses `postgresql+asyncpg://` (not `postgresql://`)
- Verify `JWT_SECRET_KEY` is set

### Frontend can't reach backend
- Check `NEXT_PUBLIC_API_URL` in Vercel env vars
- Verify CORS origins include your Vercel URL
- Check browser console for CORS errors

### Database connection refused
- Verify Supabase project is active
- Check if IP whitelist is enabled (disable for Railway)
- Verify connection string format

### Migrations fail
- Check Supabase SQL Editor for errors
- Verify PostGIS extension is enabled
- Run migrations manually if needed
