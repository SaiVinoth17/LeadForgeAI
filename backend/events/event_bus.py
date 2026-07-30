"""
Production Real-Time Event Bus for FORGE OS V5 Backend.
Dispatches system events between AI workers and WebSocket listeners.
"""

import asyncio
from typing import Dict, List, Callable, Any
from core.logger import logger


class BackendEventBus:
    """
    Asynchronous Inter-Agent Event Bus.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._websocket_listeners: List[Callable] = []

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)

    def register_ws_broadcaster(self, broadcaster: Callable):
        if broadcaster not in self._websocket_listeners:
            self._websocket_listeners.append(broadcaster)

    def publish(self, event_name: str, data: Dict[str, Any]):
        """Publishes event to Python subscribers and broadcasts to WebSockets."""
        logger.info(f"[EventBus] Published: {event_name} -> {data.get('lead_name', '')}")

        # Local Subscribers
        if event_name in self._subscribers:
            for cb in self._subscribers[event_name]:
                try:
                    cb(data)
                except Exception as e:
                    logger.error(f"[EventBus] Error in callback for {event_name}: {e}")

        # WebSocket Broadcast
        event_payload = {"event": event_name, "data": data}
        for ws_cb in self._websocket_listeners:
            try:
                if asyncio.iscoroutinefunction(ws_cb):
                    asyncio.create_task(ws_cb(event_payload))
                else:
                    ws_cb(event_payload)
            except Exception as e:
                logger.error(f"[EventBus] Error broadcasting to WS: {e}")


backend_event_bus = BackendEventBus()
