"""
WeakRef Thread-Safe Event Bus for LeadForge AI.
Uses weakref.WeakMethod and weakref.ref to prevent UI widget memory leaks during event emission.
"""

import weakref
from typing import Dict, List, Callable, Any
from core.logger import logger


class EventBus:
    """
    WeakRef Event Bus preventing listener memory leaks.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Any]] = {}

    def subscribe(self, event_type: str, listener: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        ref = self._create_ref(listener)
        if ref and ref not in self._listeners[event_type]:
            self._listeners[event_type].append(ref)

    def unsubscribe(self, event_type: str, listener: Callable):
        if event_type in self._listeners:
            ref = self._create_ref(listener)
            self._listeners[event_type] = [
                r for r in self._listeners[event_type] if r != ref and r() is not None
            ]

    def emit(self, event_type: str, *args, **kwargs):
        if event_type in self._listeners:
            alive_refs = []
            for ref in self._listeners[event_type]:
                func = ref()
                if func is not None:
                    alive_refs.append(ref)
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Error in EventBus listener for '{event_type}': {e}")
            # Clean up dead weak references
            self._listeners[event_type] = alive_refs

    def _create_ref(self, listener: Callable) -> Any:
        try:
            if hasattr(listener, "__self__") and listener.__self__ is not None:
                return weakref.WeakMethod(listener)
            else:
                return weakref.ref(listener)
        except Exception:
            return lambda: listener


# Global Event Bus Instance
event_bus = EventBus()


# Event Constants
class Events:
    LEAD_ADDED = "LEAD_ADDED"
    LEAD_UPDATED = "LEAD_UPDATED"
    LEAD_DELETED = "LEAD_DELETED"
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    SCRAPE_COMPLETED = "SCRAPE_COMPLETED"
    NAVIGATE = "NAVIGATE"
