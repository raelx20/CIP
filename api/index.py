"""Vercel serverless entry point for the FastAPI backend."""

import sys
import json
from pathlib import Path

# Add api/backend directory to Python path
backend_dir = str(Path(__file__).resolve().parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
except ImportError:
    # Minimal ASGI fallback if FastAPI import fails
    async def app(scope, receive, send):
        if scope["type"] == "http":
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            })
            body = json.dumps({"status": "error", "message": "Backend import failed"}).encode()
            await send({"type": "http.response.body", "body": body})
