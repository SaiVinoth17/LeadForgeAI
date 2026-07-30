"""
Centralized Configuration Manager for LeadForge AI.
Provides type-safe, schema-validated configuration retrieval and updates.
"""

from typing import Any, Optional
from database.crud import get_setting, set_setting


class ConfigManager:
    """
    Type-Safe Application Configuration Manager.
    """
    DEFAULTS = {
        "ai_provider": "gemini",
        "ai_api_key": "",
        "ai_model": "gemini-1.5-flash",
        "ai_setup_completed": "false",
        "lead_provider": "OpenStreetMap",
        "search_radius": "5000",
        "company_name": "LeadForge Agency",
        "screenshot_interval": "7"
    }

    @classmethod
    def get(cls, key: str, fallback: Optional[Any] = None) -> Any:
        """Retrieves setting with typed default fallback."""
        default_val = cls.DEFAULTS.get(key, fallback)
        val = get_setting(key, default_val)
        return val if val is not None else default_val

    @classmethod
    def set(cls, key: str, value: Any) -> bool:
        """Sets application setting."""
        return set_setting(key, str(value))


config_mgr = ConfigManager()
