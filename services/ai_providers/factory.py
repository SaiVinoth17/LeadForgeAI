"""
Dynamic AI Provider Factory for LeadForge AI.
Returns active AI Provider instance based on database settings.
"""

from typing import Optional
from database.crud import get_setting
from services.ai_providers.base_provider import BaseAIProvider
from services.ai_providers.gemini_provider import GeminiProvider
from services.ai_providers.groq_provider import GroqProvider
from services.ai_providers.ollama_provider import OllamaProvider
from services.ai_providers.openrouter_provider import OpenRouterProvider
from core.logger import logger


class AIProviderFactory:
    """
    Factory to retrieve active provider.
    """
    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> BaseAIProvider:
        p_name = (provider_name or get_setting("ai_provider", "gemini")).lower()

        if "groq" in p_name:
            return GroqProvider()
        elif "ollama" in p_name:
            return OllamaProvider()
        elif "openrouter" in p_name:
            return OpenRouterProvider()
        else:
            return GeminiProvider()
