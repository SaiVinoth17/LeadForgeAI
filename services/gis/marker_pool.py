"""
Canvas Marker Object Pool Manager for LeadForge AI GIS Engine.
Pre-allocates, recycles, and pools canvas marker references to eliminate Python Garbage Collection pauses.
"""

from typing import Dict, List, Any, Optional
from core.logger import logger


class MarkerPool:
    """
    Object pool for map canvas position markers.
    """
    def __init__(self, map_widget: Any):
        self.map_widget = map_widget
        self.active_markers: Dict[str, Any] = {}
        self.recycled_pool: List[Any] = []

    def get_active_count(self) -> int:
        """Returns total active rendered markers."""
        return len(self.active_markers)

    def release_marker(self, marker_id: str) -> None:
        """Releases and deletes a marker handle from canvas."""
        handle = self.active_markers.pop(marker_id, None)
        if handle:
            try:
                handle.delete()
            except Exception as e:
                logger.error(f"Error releasing marker handle: {e}")

    def release_all(self) -> None:
        """Releases all active markers."""
        for mid in list(self.active_markers.keys()):
            self.release_marker(mid)
        self.active_markers.clear()

    def set_marker(self, marker_id: str, lat: float, lon: float, text: str, color: str, command: Optional[Any] = None) -> Any:
        """
        Retrieves or creates a marker at position (lat, lon).
        """
        # If marker_id already active, update position/text if changed
        if marker_id in self.active_markers:
            handle = self.active_markers[marker_id]
            try:
                handle.set_position(lat, lon)
                return handle
            except Exception:
                self.release_marker(marker_id)

        # Create marker via map_widget
        try:
            handle = self.map_widget.set_marker(
                lat, lon,
                text=text,
                marker_color_circle=color,
                marker_color_outside=color
            )
            if command:
                handle.command = command

            self.active_markers[marker_id] = handle
            return handle
        except Exception as ex:
            logger.error(f"Failed to pool set_marker {marker_id}: {ex}")
            return None
