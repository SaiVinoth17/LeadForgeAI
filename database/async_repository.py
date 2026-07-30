"""
Asynchronous Repository Pattern for LeadForge AI Database.
Executes database queries off the UI thread via ThreadPoolExecutor.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, List, Optional
from database.crud import get_all_leads, add_lead, update_lead, delete_lead
from core.logger import logger

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AsyncDBWorker")


class AsyncLeadRepository:
    """
    Asynchronous Repository for Lead database operations.
    """
    @staticmethod
    def get_all_leads_async(callback: Callable[[List[Any]], None]) -> None:
        """Fetch all leads asynchronously without blocking main UI thread."""
        def _worker():
            try:
                leads = get_all_leads()
                callback(leads)
            except Exception as e:
                logger.error(f"Async DB fetch error: {e}")
                callback([])

        _executor.submit(_worker)

    @staticmethod
    def add_lead_async(lead_data: dict, callback: Optional[Callable[[Any], None]] = None) -> None:
        """Add a new lead asynchronously."""
        def _worker():
            new_lead = add_lead(lead_data)
            if callback:
                callback(new_lead)

        _executor.submit(_worker)

    @staticmethod
    def update_lead_async(lead_id: int, update_data: dict, callback: Optional[Callable[[Any], None]] = None) -> None:
        """Update lead record asynchronously."""
        def _worker():
            updated = update_lead(lead_id, update_data)
            if callback:
                callback(updated)

        _executor.submit(_worker)


async_repo = AsyncLeadRepository()
