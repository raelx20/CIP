"""Vercel serverless entry point for the FastAPI backend.

This file adapts the FastAPI app for Vercel's Python serverless runtime.
All /api/* requests are routed here by vercel.json.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so imports work
backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app  # noqa: E402

# Vercel Python runtime expects an ASGI app named `app`
# FastAPI is already ASGI-compatible, so this works directly
