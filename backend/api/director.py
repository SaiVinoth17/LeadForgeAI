"""
AI Director API Endpoint Module.
"""

from services.ai_director import ai_director
from services.explainable_ai import explainable_ai


def register_director_routes(app):
    @app.route("/api/v5/director", methods=["GET"])
    def get_director_recommendation():
        rec = ai_director.get_top_recommendation()
        rec["rationale"] = explainable_ai.explain("top_lead")
        return rec
