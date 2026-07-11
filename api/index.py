"""Vercel serverless entry point for the FastAPI backend."""

import sys
from pathlib import Path

# Add api/backend directory to Python path
backend_dir = str(Path(__file__).resolve().parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app  # noqa: E402
