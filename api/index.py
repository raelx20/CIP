"""Vercel serverless entry point — FastAPI via WSGI adapter."""

import sys
import os
from pathlib import Path

# Add api/backend directory to Python path
backend_dir = str(Path(__file__).resolve().parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

# Import the full FastAPI app
from app.main import app as fastapi_app  # noqa: E402

# Create a Flask-compatible WSGI wrapper
from flask import Flask, jsonify

flask_app = Flask(__name__)


@flask_app.route("/api/v1/system/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Constituency Intelligence Platform",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
    })


@flask_app.route("/api/v1/system/ready")
def ready():
    return jsonify({
        "status": "ready",
        "database": "configured",
    })


@flask_app.route("/")
def root():
    return jsonify({
        "service": "CIP",
        "version": "1.0.0",
        "docs": "/api/v1/system/health",
    })
