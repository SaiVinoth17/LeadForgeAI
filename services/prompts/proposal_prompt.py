"""
Proposal Prompt Definition for LeadForge AI Prompt Library.
"""

from typing import Dict, Any
from services.prompts.base_prompt import BasePrompt


class ProposalPrompt(BasePrompt):
    @property
    def name(self) -> str:
        return "proposal_prompt"

    @property
    def system_prompt(self) -> str:
        return (
            "You are FORGE X, Senior Sales Director and Web Consultant for LeadForge AI.\n"
            "Generate enterprise-grade, high-converting web redesign proposals for web development agencies.\n"
            "Format output clearly using markdown with Executive Summary, Technical Deficiencies, Scope of Work, and Tiered Pricing."
        )

    def build_user_prompt(self, context_data: Dict[str, Any]) -> str:
        return (
            f"Generate a web redesign proposal for {context_data.get('company_name', 'Prospect')}.\n"
            f"Category: {context_data.get('category', 'Business')}\n"
            f"Current Website: {context_data.get('website', 'None')}\n"
            f"Opportunity Score: {context_data.get('opportunity_score', 'N/A')}/100\n"
            f"Google Rating: {context_data.get('rating', 'N/A')}\n"
            f"Address: {context_data.get('address', 'N/A')}\n\n"
            f"Requirements:\n"
            f"1. Executive Summary & Value Proposition\n"
            f"2. Top 3 Technical/Design Weaknesses\n"
            f"3. Modern Tech Stack (Next.js, Tailwind, Fast APIs)\n"
            f"4. Scope of Work & Deliverables\n"
            f"5. Investment Tiers ($1,500 - $4,800 USD)"
        )
