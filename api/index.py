"""Vercel serverless entry point for the FastAPI backend."""

import sys
import json
from pathlib import Path

# Add api/backend directory to Python path
backend_dir = str(Path(__file__).resolve().parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app  # noqa: F401,F403
except ImportError as e:
    # If import fails, create a simple error handler
    import os

    class app:  # noqa: F811
        pass

    # Store error for debugging
    os.environ["CIP_IMPORT_ERROR"] = str(e)
