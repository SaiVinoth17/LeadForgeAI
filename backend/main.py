"""
FORGE OS V6 Backend Main Application Entry Point.
Aggregates all modular API route handlers from backend/api/ and serves the React frontend bundle.
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.api.director import register_director_routes
from backend.api.leads import register_leads_routes
from backend.api.copilot import register_copilot_routes
from backend.api.missions import register_missions_routes
from backend.api.health import register_health_routes
from backend.api.workflow import register_workflow_routes
from backend.api.websocket import register_websocket_routes
from backend.api.auth import register_auth_routes
from backend.api.settings import register_settings_routes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app)

# Register Modular Route Handlers (API routes match first)
register_director_routes(app)
register_leads_routes(app)
register_copilot_routes(app)
register_missions_routes(app)
register_health_routes(app)
register_workflow_routes(app)
register_websocket_routes(app)
register_auth_routes(app)
register_settings_routes(app)

# Serve Frontend SPA
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    elif os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return send_from_directory(FRONTEND_DIST, "index.html")
    else:
        return "Frontend build not found. Please run 'npm run build' in frontend directory.", 404
