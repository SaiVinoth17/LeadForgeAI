"""
Agency Copilot Assistant API Endpoint Module.
"""

from services.strategy_engine import strategy_engine
from backend.events.event_bus import backend_event_bus


def register_copilot_routes(app):
    @app.route("/api/v5/copilot/action", methods=["GET", "POST"])
    def execute_copilot_action():
        lead_name = "Blue Hills Resort"
        strat = strategy_engine.evaluate_strategy(lead_name)

        backend_event_bus.publish("proposal.started", {"lead_name": lead_name, "package": strat["recommended_package"]})

        return {
            "status": "success",
            "lead_name": lead_name,
            "strategy": strat,
            "latency_ms": 12
        }
