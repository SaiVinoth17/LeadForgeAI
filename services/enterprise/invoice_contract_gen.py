"""
Enterprise Contract & Milestone Invoice Generator for LeadForge AI.
Generates legal Web Development Agreements and 3-stage milestone invoice schedules.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from models.lead import Lead
from services.enterprise.agency_manager import agency_manager


class ContractInvoiceEngine:
    """
    Generates legal agency client contracts and milestone invoices.
    """
    @staticmethod
    def generate_services_contract(lead: Lead, agency_name: str = None) -> str:
        """Generates a legal Web Development Services Agreement."""
        agency = agency_name or agency_manager.branding.agency_name
        b_name = lead.business_name or "Client Business"
        est_val = lead.estimated_value or 65000.0
        today = datetime.utcnow().strftime("%B %d, %Y")

        contract = f"""# WEB DEVELOPMENT SERVICES AGREEMENT

**Effective Date**: {today}  
**Service Provider**: {agency}  
**Client**: {b_name}  
**Project Total**: ₹{est_val:,.2f}

---

### 1. SCOPE OF SERVICES
{agency} agrees to design, develop, test, and deploy a custom, mobile-responsive website for **{b_name}**, addressing identified security (SSL), user experience, and local discovery bottlenecks.

### 2. INVESTMENT & MILESTONE PAYMENTS
The total investment for the project is **₹{est_val:,.2f}**, payable according to the following milestone schedule:
- **Milestone 1 (50% Deposit)**: ₹{est_val * 0.50:,.2f} — Payable upon signing to initiate project.
- **Milestone 2 (25% Design Approval)**: ₹{est_val * 0.25:,.2f} — Payable upon client review of homepage design mockups.
- **Milestone 3 (25% Launch Final)**: ₹{est_val * 0.25:,.2f} — Payable upon final deployment and domain handover.

### 3. TIMELINE & DELIVERABLES
- **Phase 1 (Discovery & Architecture)**: Days 1-7
- **Phase 2 (Design & Content Creation)**: Days 8-18
- **Phase 3 (Development & SEO Integration)**: Days 19-25
- **Phase 4 (Final QA, Launch & Handover)**: Days 26-30

### 4. INTELLECTUAL PROPERTY
Upon receipt of full final payment, all website source code, design assets, and domain credentials shall transfer exclusively to **{b_name}**.

### 5. SIGNATURES

________________________________________  
**For {agency}**  
Date: {today}

________________________________________  
**For {b_name}**  
Date: {today}
"""
        return contract

    @staticmethod
    def generate_milestone_invoice(lead: Lead, milestone_index: int = 1) -> Dict[str, Any]:
        """Generates a structured payment invoice payload for a specific milestone."""
        b_name = lead.business_name or "Client Business"
        est_val = lead.estimated_value or 65000.0
        invoice_num = f"INV-{lead.id or 1001}-{milestone_index}"

        milestones = [
            ("Milestone 1: 50% Deposit & Project Commencement", 0.50),
            ("Milestone 2: 25% Design Review & UX Approval", 0.25),
            ("Milestone 3: 25% Final Deployment & Domain Handover", 0.25),
        ]

        title, percentage = milestones[min(milestone_index - 1, 2)]
        amount = est_val * percentage
        due_date = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")

        return {
            "invoice_number": invoice_num,
            "agency": agency_manager.branding.agency_name,
            "client": b_name,
            "description": title,
            "amount": amount,
            "tax": amount * 0.18,  # 18% GST standard
            "total_due": amount * 1.18,
            "due_date": due_date,
            "payment_link": f"https://{agency_manager.branding.custom_domain}/pay/{invoice_num}"
        }
