"""
Structured AI Executable Tools Registry for LeadForge AI.
Enables AI model outputs to execute database operations, CRM updates, and file exports.
"""

from typing import Dict, Any, Optional
from core.logger import logger
from database.crud import update_lead


class AIToolsRegistry:
    """
    Registry of structured tools executable by AI workflows.
    """
    @staticmethod
    def save_proposal(lead_id: int, proposal_text: str) -> Dict[str, Any]:
        """Saves generated proposal text to lead record."""
        try:
            update_lead(lead_id, {"status": "Proposal Sent", "notes": proposal_text[:300]})
            return {"status": "success", "lead_id": lead_id, "action": "save_proposal"}
        except Exception as e:
            logger.error(f"Tool error save_proposal: {e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    def save_email(lead_id: int, email_text: str) -> Dict[str, Any]:
        """Saves cold email to CRM timeline."""
        try:
            update_lead(lead_id, {"notes": f"Email Draft: {email_text[:200]}"})
            return {"status": "success", "lead_id": lead_id, "action": "save_email"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def update_crm(lead_id: int, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Updates lead status and notes in CRM."""
        try:
            kwargs = {"status": status}
            if notes:
                kwargs["notes"] = notes
            update_lead(lead_id, **kwargs)
            return {"status": "success", "lead_id": lead_id, "status_updated": status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def generate_pricing(tier: str = "professional") -> Dict[str, Any]:
        """Returns pricing structure."""
        prices = {"starter": 1500, "professional": 2800, "enterprise": 4500}
        return {"tier": tier, "price": prices.get(tier, 2800), "currency": "USD"}


ai_tools = AIToolsRegistry()
