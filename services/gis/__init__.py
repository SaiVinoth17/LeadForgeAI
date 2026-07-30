"""
GIS Engine Package for LeadForge AI.
Provides high-performance 120 FPS spatial indexing, marker virtualization, clustering,
inertial momentum physics, camera interpolation, object pooling, and performance telemetry HUD.
"""

from services.gis.spatial_index import QuadTree, Point, BoundingBox
from services.gis.cluster_engine import ClusterEngine, MapMarker
from services.gis.cache_engine import GISCacheEngine, gis_cache
from services.gis.viewport_manager import ViewportManager
from services.gis.animation_engine import Easing, InertialPhysics, CameraAnimator
from services.gis.marker_pool import MarkerPool
from services.gis.telemetry_hud import GISProfilerHUD
from services.gis.render_pipeline import FrameScheduler, frame_scheduler

__all__ = [
    "QuadTree",
    "Point",
    "BoundingBox",
    "ClusterEngine",
    "MapMarker",
    "GISCacheEngine",
    "gis_cache",
    "ViewportManager",
    "Easing",
    "InertialPhysics",
    "CameraAnimator",
    "MarkerPool",
    "GISProfilerHUD",
    "FrameScheduler",
    "frame_scheduler",
]
