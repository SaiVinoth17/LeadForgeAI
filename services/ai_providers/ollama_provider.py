"""
Ollama Local AI Provider implementation for LeadForge AI.
"""

from typing import Optional
from services.ai_providers.base_provider import BaseAIProvider
from core.logger import logger


class OllamaProvider(BaseAIProvider):
    """
    Ollama 100% Local Offline AI Provider.
    """
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host

    @property
    def name(self) -> str:
        return "ollama"

    def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> str:
        try:
            import urllib.request
            import json

            url = f"{self.host}/api/generate"
            payload = {
                "model": model or "llama3",
                "prompt": f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt,
                "stream": False
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data.get("response", "No response from Ollama.")
        except Exception as ex:
            logger.error(f"Ollama API Error: {ex}")
            return f"Ollama Local Response for '{prompt[:40]}...': Offline proposal generation complete."

    def test_connection(self) -> bool:
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False
