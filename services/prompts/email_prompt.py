"""
Cold Email Prompt Definition for LeadForge AI Prompt Library.
"""

from typing import Dict, Any
from services.prompts.base_prompt import BasePrompt


class EmailPrompt(BasePrompt):
    @property
    def name(self) -> str:
        return "email_prompt"

    @property
    def system_prompt(self) -> str:
        return "You are a Top 1% Agency Copywriter specializing in cold emails that get responses."

    def build_user_prompt(self, context_data: Dict[str, Any]) -> str:
        return (
            f"Write a personalized cold email to the owner of {context_data.get('company_name', 'Business')}.\n"
            f"Industry: {context_data.get('category', 'Local Business')}\n"
            f"Website: {context_data.get('website', 'No Website')}\n"
            f"Opportunity Score: {context_data.get('opportunity_score', 'N/A')}\n\n"
            f"Guidelines:\n"
            f"- 4 paragraphs max, punchy subject line.\n"
            f"- Mention specific mobile performance or missing website issues.\n"
            f"- Soft call to action: offer a free 3-minute video audit."
        )
