"""
WhatsApp Pitch Prompt Definition for LeadForge AI Prompt Library.
"""

from typing import Dict, Any
from services.prompts.base_prompt import BasePrompt


class WhatsAppPrompt(BasePrompt):
    @property
    def name(self) -> str:
        return "whatsapp_prompt"

    @property
    def system_prompt(self) -> str:
        return "You are a Direct Response Sales Consultant writing short WhatsApp audio/text pitches."

    def build_user_prompt(self, context_data: Dict[str, Any]) -> str:
        return (
            f"Write a 3-sentence WhatsApp pitch for {context_data.get('company_name', 'Business')}.\n"
            f"Rating: {context_data.get('rating', 'N/A')}\n"
            f"Website: {context_data.get('website', 'None')}\n"
            f"Focus on how modern mobile booking increases revenue."
        )
