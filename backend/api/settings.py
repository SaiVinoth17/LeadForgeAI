"""
Production Settings & AI Providers Configuration API Route Handlers.
"""

from flask import request

SETTINGS_STORE = {
    "general": {
        "agency_name": "LeadForge Operating Systems",
        "timezone": "Asia/Kolkata",
        "currency": "INR (₹)"
    },
    "ai_providers": {
        "gemini_key": "sk-gemini-prod-active",
        "groq_key": "gsk_groq_lpu_active",
        "ollama_url": "http://localhost:11434",
        "openrouter_key": "sk-or-v1-active",
        "active_provider": "Gemini 1.5 Flash"
    }
}


def register_settings_routes(app):
    @app.route("/api/v5/settings", methods=["GET"])
    def get_settings():
        return SETTINGS_STORE

    @app.route("/api/v5/settings", methods=["POST"])
    def update_settings():
        data = request.json or {}
        if "general" in data:
            SETTINGS_STORE["general"].update(data["general"])
        if "ai_providers" in data:
            SETTINGS_STORE["ai_providers"].update(data["ai_providers"])
        return {"status": "success", "settings": SETTINGS_STORE}
