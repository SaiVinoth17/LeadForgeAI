"""
Multi-Level Memory Cache Engine for LeadForge AI GIS.
Provides fast in-memory access to spatial leads, QuadTree indexes, and cluster results.
"""

from typing import List, Dict, Any, Optional, Tuple
import threading
from database.db_manager import db_manager
from models.lead import Lead
from services.gis.spatial_index import QuadTree, BoundingBox
from services.gis.cluster_engine import MapMarker
from core.logger import logger


class GISCacheEngine:
    """
    Thread-safe memory cache for spatial GIS data.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._lead_data_cache: List[Dict[str, Any]] = []
        self._quadtree: Optional[QuadTree] = None
        self._cluster_cache: Dict[Tuple[int, float, float, float, float], List[MapMarker]] = {}
        self._is_loaded: bool = False

    def is_loaded(self) -> bool:
        with self._lock:
            return self._is_loaded

    def load_spatial_data(self, force_reload: bool = False) -> QuadTree:
        """
        Fetches lead spatial coordinates from database and builds QuadTree.
        Returns initialized QuadTree. Thread-safe.
        """
        with self._lock:
            if self._is_loaded and not force_reload and self._quadtree is not None:
                return self._quadtree

        session = db_manager.get_session()
        lead_records: List[Dict[str, Any]] = []
        try:
            # Efficient lightweight query for lat/lon fields only
            results = (
                session.query(
                    Lead.id,
                    Lead.business_name,
                    Lead.latitude,
                    Lead.longitude,
                    Lead.opportunity_score,
                    Lead.priority,
                    Lead.category
                )
                .filter(Lead.latitude.isnot(None), Lead.longitude.isnot(None))
                .all()
            )

            for row in results:
                lead_records.append({
                    "id": row.id,
                    "business_name": row.business_name,
                    "opportunity_score": row.opportunity_score or 0,
                    "priority": row.priority or "Low",
                    "category": row.category or "General"
                }, )
                # Save lat/lon in dict list for tree building
                lead_records[-1]["lat"] = float(row.latitude)
                lead_records[-1]["lon"] = float(row.longitude)

        except Exception as e:
            logger.error(f"Failed to load spatial leads from DB: {e}")
        finally:
            session.close()

        # Build QuadTree spatial index
        qtree = QuadTree(BoundingBox(-90.0, 90.0, -180.0, 180.0), capacity=32)
        for rec in lead_records:
            qtree.insert(rec["lat"], rec["lon"], rec)

        with self._lock:
            self._lead_data_cache = lead_records
            self._quadtree = qtree
            self._cluster_cache.clear()
            self._is_loaded = True
            logger.info(f"GISCacheEngine loaded {len(lead_records)} spatial points into QuadTree.")

        return qtree

    def get_quadtree(self) -> QuadTree:
        """Returns active QuadTree index (loads from DB if not ready)."""
        if not self.is_loaded():
            return self.load_spatial_data()
        with self._lock:
            return self._quadtree or QuadTree()

    def get_cached_cluster(self, key: Tuple[int, float, float, float, float]) -> Optional[List[MapMarker]]:
        """Retrieves cached cluster output for a specific zoom/bbox key."""
        with self._lock:
            return self._cluster_cache.get(key)

    def set_cached_cluster(self, key: Tuple[int, float, float, float, float], markers: List[MapMarker]) -> None:
        """Caches cluster output for a given key (bounded size)."""
        with self._lock:
            if len(self._cluster_cache) > 200:
                self._cluster_cache.clear()
            self._cluster_cache[key] = markers

    def invalidate() -> None:
        """Invalidates cache forcing reload on next request."""
        with self._lock:
            self._is_loaded = False
            self._quadtree = None
            self._cluster_cache.clear()
            self._lead_data_cache.clear()


# Global cache instance singleton
gis_cache = GISCacheEngine()
