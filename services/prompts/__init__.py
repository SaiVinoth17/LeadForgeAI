"""
Prompt Library Package for LeadForge AI.
"""

from services.prompts.base_prompt import BasePrompt
from services.prompts.proposal_prompt import ProposalPrompt
from services.prompts.email_prompt import EmailPrompt
from services.prompts.whatsapp_prompt import WhatsAppPrompt

__all__ = [
    "BasePrompt",
    "ProposalPrompt",
    "EmailPrompt",
    "WhatsAppPrompt",
]
