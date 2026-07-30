"""
Leads & Digital Twin API Endpoint Module.
"""

from database.crud import get_all_leads
from services.memory_engine import memory_engine


def register_leads_routes(app):
    @app.route("/api/v5/leads", methods=["GET"])
    def get_leads():
        leads = get_all_leads()
        result = []
        for l in leads:
            mem = memory_engine.get_client_memory(l.business_name)
            result.append({
                "id": l.id,
                "business_name": l.business_name,
                "category": l.category,
                "website": l.website,
                "score": l.opportunity_score or 90,
                "digital_twin": mem
            })
        return result
