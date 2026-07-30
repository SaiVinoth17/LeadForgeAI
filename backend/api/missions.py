"""
Mission Control API Endpoint Module.
"""

from services.mission_engine import mission_engine


def register_missions_routes(app):
    @app.route("/api/v5/missions", methods=["GET"])
    def get_active_missions():
        return mission_engine.get_active_mission()
