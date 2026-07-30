"""
Async Viewport Manager for LeadForge AI GIS Engine.
Provides debounced event handling, bounding box buffering, and incremental marker diffing.
"""

from typing import Dict, List, Set, Tuple, Any, Callable, Optional
import threading
from concurrent.futures import ThreadPoolExecutor
from services.gis.cache_engine import gis_cache
from services.gis.cluster_engine import ClusterEngine, MapMarker
from core.logger import logger


class ViewportManager:
    """
    Manages spatial viewport queries asynchronously with incremental rendering diffs.
    """
    def __init__(self, debounce_ms: int = 30):
        self.debounce_ms = debounce_ms
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="GISViewport")
        self._debounce_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._active_marker_ids: Set[str] = set()

    def update_viewport(
        self,
        top_lat: float,
        left_lon: float,
        bottom_lat: float,
        right_lon: float,
        zoom_level: int,
        on_diff_computed: Callable[[Set[str], List[MapMarker]], None]
    ) -> None:
        """
        Debounces and dispatches async background worker task for viewport calculation.
        """
        with self._lock:
            if self._debounce_timer is not None:
                self._debounce_timer.cancel()

            self._debounce_timer = threading.Timer(
                self.debounce_ms / 1000.0,
                self._dispatch_task,
                args=(top_lat, left_lon, bottom_lat, right_lon, zoom_level, on_diff_computed)
            )
            self._debounce_timer.daemon = True
            self._debounce_timer.start()

    def _dispatch_task(
        self,
        top_lat: float,
        left_lon: float,
        bottom_lat: float,
        right_lon: float,
        zoom_level: int,
        on_diff_computed: Callable[[Set[str], List[MapMarker]], None]
    ) -> None:
        """Executes computation in background ThreadPoolExecutor."""
        self._executor.submit(
            self._compute_viewport_diff,
            top_lat, left_lon, bottom_lat, right_lon, zoom_level, on_diff_computed
        )

    def _compute_viewport_diff(
        self,
        top_lat: float,
        left_lon: float,
        bottom_lat: float,
        right_lon: float,
        zoom_level: int,
        on_diff_computed: Callable[[Set[str], List[MapMarker]], None]
    ) -> None:
        """Background thread worker to query spatial index, cluster, and compute incremental diffs."""
        try:
            # Padded bounding box calculation (15% margin buffer)
            lat_span = abs(top_lat - bottom_lat)
            lon_span = abs(right_lon - left_lon)
            lat_buffer = max(0.01, lat_span * 0.15)
            lon_buffer = max(0.01, lon_span * 0.15)

            min_lat = min(top_lat, bottom_lat) - lat_buffer
            max_lat = max(top_lat, bottom_lat) + lat_buffer
            min_lon = min(left_lon, right_lon) - lon_buffer
            max_lon = max(left_lon, right_lon) + lon_buffer

            # Generate cache key (rounded to 2 decimal places to utilize cache hits during micro-panning)
            cache_key = (
                int(zoom_level),
                round(min_lat, 2),
                round(max_lat, 2),
                round(min_lon, 2),
                round(max_lon, 2)
            )

            markers = gis_cache.get_cached_cluster(cache_key)
            if markers is None:
                qtree = gis_cache.get_quadtree()
                points = qtree.query_range(min_lat, max_lat, min_lon, max_lon)
                markers = ClusterEngine.cluster_points(points, zoom_level)
                gis_cache.set_cached_cluster(cache_key, markers)

            # Compute incremental diffs
            target_ids = {m.marker_id: m for m in markers}

            with self._lock:
                to_remove = self._active_marker_ids - set(target_ids.keys())
                to_add = [m for mid, m in target_ids.items() if mid not in self._active_marker_ids]
                # Update tracking set
                self._active_marker_ids = set(target_ids.keys())

            # Notify UI thread with compute diffs
            on_diff_computed(to_remove, to_add)

        except Exception as e:
            logger.error(f"Error computing viewport diff: {e}")

    def reset(self) -> None:
        """Resets active tracking markers."""
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._active_marker_ids.clear()
