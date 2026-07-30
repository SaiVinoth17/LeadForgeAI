"""
Agency White-Label & Multi-Workspace Manager for LeadForge AI.
Handles enterprise tier feature gating ($29, $99, $199, $299), custom branding, and client portal tokens.
"""

from typing import Dict, Any, Optional
from enum import Enum
import uuid
import json
from dataclasses import dataclass, asdict
from core.logger import logger


class SubscriptionTier(Enum):
    STARTER = "Starter ($29/mo)"
    AGENCY_PRO = "Agency Pro ($99/mo)"
    GROWTH = "Growth ($199/mo)"
    ENTERPRISE = "Enterprise White-Label ($299/mo)"


@dataclass
class AgencyBranding:
    agency_name: str = "LeadForge Agency"
    logo_url: str = ""
    primary_color: str = "#6E5BFF"
    accent_color: str = "#00E5FF"
    custom_domain: str = "portal.leadforge.ai"
    footer_text: str = "Powered by LeadForge AI Platform"
    white_label_enabled: bool = False


class AgencyManager:
    """
    Manages multi-workspace configuration, white-label settings, and tier feature permissions.
    """
    TIER_LIMITS = {
        SubscriptionTier.STARTER: {
            "max_leads_per_month": 500,
            "can_export_pdf": True,
            "can_use_copilot": True,
            "can_use_gis_map": True,
            "white_label": False,
            "multi_workspace": False,
            "team_members": 1
        },
        SubscriptionTier.AGENCY_PRO: {
            "max_leads_per_month": 2500,
            "can_export_pdf": True,
            "can_use_copilot": True,
            "can_use_gis_map": True,
            "white_label": False,
            "multi_workspace": True,
            "team_members": 5
        },
        SubscriptionTier.GROWTH: {
            "max_leads_per_month": 10000,
            "can_export_pdf": True,
            "can_use_copilot": True,
            "can_use_gis_map": True,
            "white_label": True,
            "multi_workspace": True,
            "team_members": 15
        },
        SubscriptionTier.ENTERPRISE: {
            "max_leads_per_month": 50000,
            "can_export_pdf": True,
            "can_use_copilot": True,
            "can_use_gis_map": True,
            "white_label": True,
            "multi_workspace": True,
            "team_members": 999
        }
    }

    def __init__(self, tier: SubscriptionTier = SubscriptionTier.AGENCY_PRO):
        self.current_tier = tier
        self.branding = AgencyBranding()

    def set_tier(self, tier: SubscriptionTier) -> None:
        """Sets active subscription tier."""
        self.current_tier = tier
        logger.info(f"AgencyManager tier updated to: {tier.value}")

    def update_branding(
        self,
        agency_name: str,
        logo_url: str = "",
        primary_color: str = "#6E5BFF",
        custom_domain: str = "",
        white_label_enabled: bool = False
    ) -> AgencyBranding:
        """Updates agency white-label branding configuration."""
        if white_label_enabled and not self.is_feature_allowed("white_label"):
            logger.warning(f"White-labeling is not allowed on {self.current_tier.value}")
            white_label_enabled = False

        self.branding = AgencyBranding(
            agency_name=agency_name,
            logo_url=logo_url,
            primary_color=primary_color,
            custom_domain=custom_domain,
            white_label_enabled=white_label_enabled
        )
        logger.info(f"Updated agency branding for: {agency_name}")
        return self.branding

    def is_feature_allowed(self, feature_key: str) -> bool:
        """Checks if a feature is permitted under the active subscription tier."""
        limits = self.TIER_LIMITS.get(self.current_tier, {})
        return limits.get(feature_key, False)

    def generate_client_portal_token(self, lead_id: int) -> str:
        """Generates a secure, unique client portal access token for proposal sharing."""
        portal_id = uuid.uuid4().hex[:12]
        return f"https://{self.branding.custom_domain}/portal/view/{portal_id}?lead={lead_id}"

    def export_config_json(self) -> str:
        """Exports agency settings as a JSON payload."""
        payload = {
            "tier": self.current_tier.value,
            "limits": self.TIER_LIMITS[self.current_tier],
            "branding": asdict(self.branding)
        }
        return json.dumps(payload, indent=2)


agency_manager = AgencyManager()
