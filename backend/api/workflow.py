"""
Autonomous Workflow Engine API Endpoint Module.
"""

from services.workflow_engine import workflow_engine


def register_workflow_routes(app):
    @app.route("/api/v5/workflow/status", methods=["GET"])
    def get_workflow_status():
        return {
            "current_stage": "Stage 4: Cold Email Generation",
            "progress": 0.65,
            "pipeline": [
                {"stage": "Website Audit", "status": "Completed"},
                {"stage": "SEO Analysis", "status": "Completed"},
                {"stage": "Proposal", "status": "Completed"},
                {"stage": "Cold Email", "status": "Running"},
                {"stage": "Contract", "status": "Waiting"},
            ]
        }
