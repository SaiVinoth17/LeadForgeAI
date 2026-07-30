"""
Abstract Base Class for AI Providers in LeadForge AI.
Enforces a uniform interface across Gemini, Groq, Ollama, and OpenRouter.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAIProvider(ABC):
    """
    Abstract AI Provider interface.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns provider identifier name."""
        pass

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> str:
        """
        Generates text response for prompt.
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Tests API connectivity.
        """
        pass
