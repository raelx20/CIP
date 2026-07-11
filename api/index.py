"""Vercel serverless entry point — Flask health endpoint."""

import os
import json
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/v1/system/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Constituency Intelligence Platform",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
    })


@app.route("/api/v1/system/ready")
def ready():
    return jsonify({
        "status": "ready",
        "database": "configured",
    })


@app.route("/")
def root():
    return jsonify({
        "service": "CIP",
        "version": "1.0.0",
        "docs": "/api/v1/system/health",
    })
