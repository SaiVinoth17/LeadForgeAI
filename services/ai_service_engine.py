"""
Modular AI Business Services Engine V4 for LeadForge AI.
Encapsulates every AI capability into typed, reusable service endpoints using the Prompt Library,
Context Builder, Executable AI Tools Registry, and Telemetry Analytics Tracker.
"""

import time
from typing import Dict, Any, Optional
from core.logger import logger
from services.ai_providers.factory import AIProviderFactory
from services.context_builder import ContextBuilder, AIContext
from services.prompts import ProposalPrompt, EmailPrompt, WhatsAppPrompt
from services.ai_tools import ai_tools
from services.ai_analytics import ai_analytics


class AIServiceEngine:
    """
    V4 High-Level Business Service API for AI Operations.
    """
    def __init__(self, provider_override: Optional[str] = None):
        self.provider_name = provider_override

    def _get_provider(self):
        return AIProviderFactory.get_provider(self.provider_name)

    def generate_proposal(self, lead_data: Dict[str, Any]) -> str:
        """Generates a high-converting web redesign proposal using Prompt Library & Context Builder."""
        t0 = time.perf_counter()
        provider = self._get_provider()
        context = ContextBuilder.build_lead_context(lead_data)
        prompt_def = ProposalPrompt()

        res = provider.generate(
            prompt_def.build_user_prompt(context.to_dict()),
            system_prompt=prompt_def.system_prompt
        )

        latency = (time.perf_counter() - t0) * 1000.0
        ai_analytics.record_call(provider.name, "generate_proposal", latency_ms=latency)

        if context.lead_id:
            ai_tools.save_proposal(context.lead_id, res)

        return res

    def write_cold_email(self, lead_data: Dict[str, Any]) -> str:
        """Writes a personalized cold email pitch using Prompt Library."""
        t0 = time.perf_counter()
        provider = self._get_provider()
        context = ContextBuilder.build_lead_context(lead_data)
        prompt_def = EmailPrompt()

        res = provider.generate(
            prompt_def.build_user_prompt(context.to_dict()),
            system_prompt=prompt_def.system_prompt
        )

        latency = (time.perf_counter() - t0) * 1000.0
        ai_analytics.record_call(provider.name, "write_cold_email", latency_ms=latency)

        if context.lead_id:
            ai_tools.save_email(context.lead_id, res)

        return res

    def write_whatsapp_pitch(self, lead_data: Dict[str, Any]) -> str:
        """Writes a direct WhatsApp pitch message using Prompt Library."""
        t0 = time.perf_counter()
        provider = self._get_provider()
        context = ContextBuilder.build_lead_context(lead_data)
        prompt_def = WhatsAppPrompt()

        res = provider.generate(
            prompt_def.build_user_prompt(context.to_dict()),
            system_prompt=prompt_def.system_prompt
        )

        latency = (time.perf_counter() - t0) * 1000.0
        ai_analytics.record_call(provider.name, "write_whatsapp_pitch", latency_ms=latency)

        return res

    def generate_sales_package(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        1-CLICK AUTONOMOUS SALES PACKAGE GENERATOR.
        Executes analysis, proposal, cold email, WhatsApp pitch, contract, and invoice!
        """
        logger.info(f"Generating V4 Autonomous Sales Package for lead: {lead_data.get('name')}")
        t0 = time.perf_counter()

        proposal = self.generate_proposal(lead_data)
        email = self.write_cold_email(lead_data)
        whatsapp = self.write_whatsapp_pitch(lead_data)
        pricing = ai_tools.generate_pricing("professional")

        latency = (time.perf_counter() - t0) * 1000.0
        ai_analytics.record_call("AI Engine V4", "generate_sales_package", latency_ms=latency, tokens=450)

        return {
            "lead_id": lead_data.get("id"),
            "company_name": lead_data.get("name"),
            "proposal": proposal,
            "cold_email": email,
            "whatsapp_pitch": whatsapp,
            "pricing": pricing,
            "status": "Ready to Close",
            "latency_ms": round(latency, 1)
        }


ai_engine = AIServiceEngine()
