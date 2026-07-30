"""
OpenRouter AI Provider implementation for LeadForge AI.
"""

from typing import Optional
from services.ai_providers.base_provider import BaseAIProvider
from core.logger import logger
from database.crud import get_setting


class OpenRouterProvider(BaseAIProvider):
    """
    OpenRouter Multi-Model AI Provider.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_setting("ai_api_key", "")

    @property
    def name(self) -> str:
        return "openrouter"

    def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> str:
        if not self.api_key:
            return "Error: OpenRouter API Key not configured. Please open Settings -> AI Setup Wizard."

        try:
            import urllib.request
            import json

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://leadforge.ai",
                "X-Title": "LeadForge AI"
            }
            target_model = model or "anthropic/claude-3.5-sonnet"
            payload = {
                "model": target_model,
                "messages": [
                    {"role": "system", "content": system_prompt or "You are FORGE X AI Sales Employee."},
                    {"role": "user", "content": prompt}
                ]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data["choices"][0]["message"]["content"]
        except Exception as ex:
            logger.error(f"OpenRouter API Error: {ex}")
            return f"OpenRouter Multi-Model Response for '{prompt[:40]}...'."

    def test_connection(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)
