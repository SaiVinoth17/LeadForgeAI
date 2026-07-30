import sqlite3
import datetime
from pathlib import Path
from core.config import DATA_DIR
from core.logger import logger

class CapabilitiesRegistry:
    """
    The FORGE OS Capabilities Registry.
    Defines exactly what data and actions the AI Engine can access.
    """
    def __init__(self):
        self.db_path = DATA_DIR / "leadforge.db"
        
    def _get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def get_crm_metrics(self) -> dict:
        """Returns key metrics for the Daily Briefing and performance analysis."""
        metrics = {}
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                metrics["total_leads"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM leads WHERE priority = 'High Opportunity'")
                metrics["high_priority"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM leads WHERE website_type = 'None'")
                metrics["no_website"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM leads WHERE website_type IN ('Facebook', 'Instagram', 'WhatsApp') OR has_ssl = 'No' OR is_mobile_responsive = 'No'")
                metrics["poor_website"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(estimated_value) FROM leads")
                metrics["pipeline_value"] = cursor.fetchone()[0] or 0.0
                
                # We do not have followup_date, so we skip overdue_followups for now.
        except Exception as e:
            logger.error(f"Error fetching CRM metrics: {e}")
            metrics["error"] = str(e)
            
        return metrics

    def get_top_opportunities(self, limit: int = 5) -> list:
        """Returns the highest ranked leads ordered by opportunity score."""
        leads = []
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, business_name, opportunity_score, category, website_type, estimated_value FROM leads ORDER BY opportunity_score DESC LIMIT ?", (limit,))
                for row in cursor.fetchall():
                    leads.append(dict(row))
        except Exception as e:
            logger.error(f"Error fetching top opportunities: {e}")
            
        return leads

    def get_available_tools(self) -> list:
        """Returns a registry of all available tools for the Planning Engine."""
        return [
            {
                "name": "get_crm_metrics",
                "description": "Retrieves real-time counts of leads, pipeline value, and website opportunities."
            },
            {
                "name": "get_top_opportunities",
                "description": "Retrieves the highest scoring leads to prioritize outreach."
            }
        ]

registry = CapabilitiesRegistry()
