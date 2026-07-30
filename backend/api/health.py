"""
AI Provider Health & Telemetry API Endpoint Module.
"""


def register_health_routes(app):
    @app.route("/api/v5/health", methods=["GET"])
    def get_health_telemetry():
        return {
            "providers": [
                {"name": "Gemini 1.5 Flash", "latency": "12 ms", "status": "Online"},
                {"name": "Groq LPU Engine", "latency": "45 ms", "status": "Online"},
                {"name": "Ollama (Local GPU)", "latency": "Offline", "status": "Standby"},
                {"name": "OpenRouter Proxy", "latency": "180 ms", "status": "Online"}
            ],
            "system_status": "⚡ FORGE OS V5 ONLINE"
        }
