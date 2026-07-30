"""
Automated AI Context Builder for LeadForge AI.
Assembles rich structured context from database leads, CRM timeline, audits, and agency preferences.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from database.crud import get_setting


@dataclass
class AIContext:
    """
    Structured Context Container for AI Invocations.
    """
    lead_id: Optional[int] = None
    company_name: str = "Prospect"
    category: str = "Business"
    website: str = ""
    rating: float = 0.0
    address: str = ""
    opportunity_score: int = 70
    agency_name: str = "My Web Agency"
    crm_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "company_name": self.company_name,
            "category": self.category,
            "website": self.website,
            "rating": self.rating,
            "address": self.address,
            "opportunity_score": self.opportunity_score,
            "agency_name": self.agency_name,
            "crm_notes": self.crm_notes,
            **self.metadata
        }


class ContextBuilder:
    """
    Assembles AIContext from raw lead dictionary or database models.
    """
    @staticmethod
    def build_lead_context(lead_data: Dict[str, Any]) -> AIContext:
        agency = get_setting("company_name", "LeadForge Agency")
        opp_score = lead_data.get("opportunity_score")
        if opp_score is None:
            opp_score = 90 if not lead_data.get("website") else 70

        return AIContext(
            lead_id=lead_data.get("id"),
            company_name=lead_data.get("name", "Prospect"),
            category=lead_data.get("category", "Local Business"),
            website=lead_data.get("website", ""),
            rating=float(lead_data.get("rating", 0.0) or 0.0),
            address=lead_data.get("address", ""),
            opportunity_score=opp_score,
            agency_name=agency,
            crm_notes=lead_data.get("notes", ""),
            metadata=lead_data
        )
