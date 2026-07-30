import pandas as pd
from core.config import EXPORTS_DIR
from core.logger import logger
from database.crud import get_all_leads
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class Exporter:
    def __init__(self):
        self.output_dir = EXPORTS_DIR
        import os
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def _leads_to_dataframe(self):
        leads = get_all_leads()
        data = []
        for lead in leads:
            data.append({
                "ID": lead.id,
                "OSM ID": getattr(lead, "osm_id", ""),
                "Business Name": lead.business_name,
                "Provider": getattr(lead, "provider", ""),
                "Category": lead.category,
                "Status": lead.status,
                "Priority": getattr(lead, "priority", ""),
                "Opportunity Score": getattr(lead, "opportunity_score", 0),
                "Estimated Value": getattr(lead, "estimated_value", ""),
                "Phone": lead.phone,
                "Email": lead.email,
                "Website": lead.website,
                "City": lead.city,
                "Rating": lead.rating,
                "Proposal Ready": "Yes" if getattr(lead, "proposal", "") else "No",
                "Email Draft": getattr(lead, "email_draft", ""),
                "WhatsApp Draft": getattr(lead, "whatsapp_draft", ""),
                "Screenshot Path": getattr(lead, "screenshot_path", ""),
                "Created Date": lead.created_date.strftime("%Y-%m-%d") if lead.created_date else ""
            })
        return pd.DataFrame(data)

    def export_csv(self, filename="leads_export.csv"):
        try:
            df = self._leads_to_dataframe()
            filepath = self.output_dir / filename
            df.to_csv(filepath, index=False)
            logger.info(f"Exported to CSV: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return None

    def export_excel(self, filename="leads_export.xlsx"):
        try:
            df = self._leads_to_dataframe()
            filepath = self.output_dir / filename
            df.to_excel(filepath, index=False, engine='openpyxl')
            logger.info(f"Exported to Excel: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export Excel: {e}")
            return None

    def export_json(self, filename="leads_export.json"):
        try:
            df = self._leads_to_dataframe()
            filepath = self.output_dir / filename
            df.to_json(filepath, orient="records", indent=4)
            logger.info(f"Exported to JSON: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return None

    def export_pdf(self, filename="leads_report.pdf"):
        try:
            filepath = self.output_dir / filename
            doc = SimpleDocTemplate(str(filepath), pagesize=landscape(letter))
            elements = []
            
            styles = getSampleStyleSheet()
            elements.append(Paragraph("LeadForge AI - CRM Report", styles['Title']))
            
            df = self._leads_to_dataframe()
            if df.empty:
                elements.append(Paragraph("No leads found.", styles['Normal']))
                doc.build(elements)
                return filepath
                
            # Limit columns for PDF fitting
            pdf_df = df[['Business Name', 'Category', 'Provider', 'Opportunity Score', 'Phone']]
            
            data = [pdf_df.columns.values.tolist()] + pdf_df.values.tolist()
            
            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B82F6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(t)
            doc.build(elements)
            logger.info(f"Exported to PDF: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            return None

    def export_client_package(self, lead):
        """Exports a full client folder with proposal, scripts, and details."""
        import os
        from pathlib import Path
        import shutil
        
        try:
            safe_name = "".join([c if c.isalnum() else "_" for c in lead.business_name])
            folder_path = self.output_dir / f"{safe_name}_Opportunity"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                
            # Business Details
            details = f"Business Name: {lead.business_name}\n"
            details += f"Category: {lead.category}\n"
            details += f"Opportunity Score: {lead.opportunity_score}/100\n"
            details += f"Priority: {lead.priority}\n"
            details += f"Confidence: {lead.confidence_score}%\n"
            details += f"Reasons: {lead.ai_summary}\n"
            
            with open(folder_path / "Business_Details.txt", "w", encoding="utf-8") as f:
                f.write(details)
                
            # Proposal
            if lead.proposal:
                with open(folder_path / "Proposal.md", "w", encoding="utf-8") as f:
                    f.write(lead.proposal)
                    
            # Outreach
            if lead.email_draft or lead.whatsapp_draft or lead.call_script:
                outreach = "=== EMAIL ===\n\n" + (lead.email_draft or "") + "\n\n"
                outreach += "=== WHATSAPP ===\n\n" + (lead.whatsapp_draft or "") + "\n\n"
                outreach += "=== CALL SCRIPT ===\n\n" + (lead.call_script or "")
                
                with open(folder_path / "Outreach_Scripts.txt", "w", encoding="utf-8") as f:
                    f.write(outreach)
                    
            if lead.screenshot_path and os.path.exists(lead.screenshot_path):
                shutil.copy(lead.screenshot_path, folder_path / "Website_Screenshot.png")
                
            logger.info(f"Exported client package to: {folder_path}")
            return folder_path
        except Exception as e:
            logger.error(f"Failed to export client package: {e}")
            return None
