"""Minimal Vercel Python endpoint — health check only."""

from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {
            "status": "healthy",
            "service": "Constituency Intelligence Platform",
            "version": "1.0.0",
            "environment": os.environ.get("ENVIRONMENT", "development"),
        }
        self.wfile.write(json.dumps(response).encode())
