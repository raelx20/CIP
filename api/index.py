"""Vercel serverless entry point — FastAPI ASGI export."""

import sys
import os
from pathlib import Path

# Add api/backend and root backend directory to Python path for serverless environment
api_backend_dir = str(Path(__file__).resolve().parent / "backend")
if api_backend_dir not in sys.path:
    sys.path.insert(0, api_backend_dir)

root_backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if root_backend_dir not in sys.path:
    sys.path.insert(0, root_backend_dir)

try:
    # pyrefly: ignore [missing-import]
    from app.main import app
except ModuleNotFoundError:
    from backend.app.main import app

# Export ASGI app directly for @vercel/python
__all__ = ["app"]

