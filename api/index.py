"""Vercel serverless entry point for the FastAPI backend."""

import sys
import os
from pathlib import Path

# Add api/backend directory to Python path
backend_dir = str(Path(__file__).resolve().parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
except Exception as e:
    # Fallback: return error as JSON if import fails
    import json
    from http.server import BaseHTTPRequestHandler

    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = {
                "status": "error",
                "message": str(e),
                "type": type(e).__name__,
            }
            self.wfile.write(json.dumps(error_response).encode())
