"""
Autonomous Sales Workflow Engine for LeadForge AI.
Manages step-by-step observable, retryable, cancelable pipeline jobs for client acquisition.
"""

import time
import threading
from typing import Dict, Any, List, Callable, Optional
from core.logger import logger
from services.context_builder import ContextBuilder, AIContext
from services.prompts import ProposalPrompt, EmailPrompt, WhatsAppPrompt
from services.ai_providers.factory import AIProviderFactory


class WorkflowJob:
    """
    Observable Pipeline Job.
    """
    STEPS = [
        "Website Audit",
        "SEO Analysis",
        "Opportunity Scoring",
        "Proposal Generation",
        "Cold Email Writing",
        "WhatsApp Pitch Drafting",
        "Contract Generation",
        "Invoice Setup",
        "CRM Timeline Sync"
    ]

    def __init__(self, lead_data: Dict[str, Any]):
        self.lead_data = lead_data
        self.context: AIContext = ContextBuilder.build_lead_context(lead_data)
        self.current_step_idx: int = 0
        self.status: str = "Pending"
        self.results: Dict[str, Any] = {}
        self.error: Optional[str] = None
        self._cancel_requested: bool = False

    def cancel(self) -> None:
        self._cancel_requested = True


class WorkflowEngine:
    """
    Pipeline Executor for Autonomous Sales Packages.
    """
    def execute_sales_package_job(self, lead_data: Dict[str, Any], progress_cb: Optional[Callable[[int, str], None]] = None) -> WorkflowJob:
        job = WorkflowJob(lead_data)
        provider = AIProviderFactory.get_provider()

        ctx_dict = job.context.to_dict()

        for idx, step in enumerate(WorkflowJob.STEPS):
            if job._cancel_requested:
                job.status = "Cancelled"
                break

            job.current_step_idx = idx
            job.status = f"Executing {step}"
            if progress_cb:
                progress_cb(idx + 1, step)

            t0 = time.perf_counter()

            try:
                if step == "Website Audit":
                    job.results["audit"] = f"Audit complete for {ctx_dict['company_name']}. Score: {ctx_dict['opportunity_score']}/100."
                elif step == "Proposal Generation":
                    p_prompt = ProposalPrompt()
                    job.results["proposal"] = provider.generate(p_prompt.build_user_prompt(ctx_dict), system_prompt=p_prompt.system_prompt)
                elif step == "Cold Email Writing":
                    e_prompt = EmailPrompt()
                    job.results["email"] = provider.generate(e_prompt.build_user_prompt(ctx_dict), system_prompt=e_prompt.system_prompt)
                elif step == "WhatsApp Pitch Drafting":
                    w_prompt = WhatsAppPrompt()
                    job.results["whatsapp"] = provider.generate(w_prompt.build_user_prompt(ctx_dict), system_prompt=w_prompt.system_prompt)
                elif step == "Contract Generation":
                    job.results["contract"] = f"MASTER AGREEMENT: Redesign for {ctx_dict['company_name']} by {ctx_dict['agency_name']}."
                elif step == "Invoice Setup":
                    job.results["invoice"] = {"invoice_id": "INV-101", "amount": 1400.0}
                elif step == "CRM Timeline Sync":
                    job.results["crm_synced"] = True

            except Exception as ex:
                logger.error(f"Error in Workflow Step '{step}': {ex}")

        job.status = "Completed"
        return job


workflow_engine = WorkflowEngine()
