"""
Base Prompt Class for LeadForge AI Prompt Library.
Decouples prompt engineering from business logic and UI code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePrompt(ABC):
    """
    Abstract Base Class for all Prompt Definitions.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the prompt."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt instructions."""
        pass

    @abstractmethod
    def build_user_prompt(self, context_data: Dict[str, Any]) -> str:
        """Assembles user prompt from structured context data."""
        pass
