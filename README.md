# CIP - Constituency Intelligence Platform

AI-powered platform for managing citizen development requests, connecting community voices with actionable intelligence for informed governance.

**Live Demo:** [cip-app-mu.vercel.app](https://cip-app-mu.vercel.app)

## Features

- **AI Chatbot** — Multilingual AI assistant helps citizens report issues conversationally
- **Issue Tracking** — Automatic categorization, deduplication, and clustering of reports
- **Geospatial Analytics** — Map-based visualization of issue hotspots and density
- **Role-Based Dashboards** — Tailored views for Citizens, MPs, Officers, and Admins
- **AI Copilot** — Decision-support assistant for administrators and elected representatives
- **Priority Scoring** — Automated severity and urgency ranking with explainable scores

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic |
| Database | PostgreSQL + PostGIS (geospatial) |
| Cache | Redis |
| LLM | Ollama (local) / OpenAI-compatible API |
| Deployment | Vercel (frontend + serverless API) |

## Project Structure

```
CIP/
├── frontend/          # Next.js frontend application
│   ├── src/app/       # Route-based pages (App Router)
│   └── src/lib/       # API client, auth context
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── domain/    # Domain models and value objects
│   │   ├── application/  # Business logic and workflows
│   │   ├── infrastructure/  # LLM, database adapters
│   │   └── prompts/   # LLM system prompts
│   └── migrations/    # Alembic database migrations
├── api/               # Vercel serverless function entry point
└── scripts/           # Utility scripts
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL with PostGIS (or use Docker)
- [Ollama](https://ollama.com/download) (for local LLM)

### Quick Start with Docker

```bash
git clone https://github.com/raelx20/CIP.git
cd CIP

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

**1. Database**
```bash
# Start PostgreSQL with PostGIS
docker run -d --name cip-db -p 5432:5432 -e POSTGRES_DB=cip -e POSTGRES_PASSWORD=postgres postgis/postgis:16-3.4
```

**2. Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r ../requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your DATABASE_URL, JWT_SECRET_KEY, etc.

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

**3. Frontend**
```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

**4. LLM (Ollama)**
```bash
ollama pull qwen3:1.7b
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection (`postgresql+asyncpg://...`) |
| `JWT_SECRET_KEY` | Yes | Secret for JWT token signing |
| `REDIS_URL` | No | Redis connection (`redis://localhost:6379/0`) |
| `LLM_BASE_URL` | No | LLM endpoint (default: `http://localhost:11434/v1`) |
| `LLM_API_KEY` | No | LLM API key (default: `ollama`) |
| `LLM_MODEL` | No | LLM model (default: `qwen3:1.7b`) |
| `NEXT_PUBLIC_API_URL` | No | Frontend API base URL |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/citizen/chat` | AI chatbot conversation |
| POST | `/api/v1/citizen/submissions` | Submit an issue |
| GET | `/api/v1/citizen/my-issues` | Get citizen's issues |
| GET | `/api/v1/mp/dashboard` | MP dashboard data |
| GET | `/api/v1/mp/priorities` | Priority rankings |
| POST | `/api/v1/mp/copilot` | AI copilot for MPs |
| GET | `/api/v1/admin/dashboard` | Admin dashboard data |

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment guide (Vercel + Supabase).

## License

Private repository. All rights reserved.
