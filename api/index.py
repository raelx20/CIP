"""Vercel serverless entry point — FastAPI ASGI export."""

import sys
from pathlib import Path

# Add backend directory to Python path for serverless environment
backend_dir = str(Path(__file__).resolve().parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

root_backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if root_backend_dir not in sys.path:
    sys.path.insert(0, root_backend_dir)

from app.main import app  # noqa: E402

__all__ = ["app"]

