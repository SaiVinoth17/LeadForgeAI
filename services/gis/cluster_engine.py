"""
Hierarchical Marker Clustering Engine for LeadForge AI GIS Engine.
Groups spatially proximate markers dynamically based on map zoom resolution.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import math
from services.gis.spatial_index import Point


@dataclass(slots=True)
class MapMarker:
    """Represents a renderable marker object (either individual or cluster)."""
    marker_id: str
    lat: float
    lon: float
    is_cluster: bool
    count: int
    text: str
    color: str
    opportunity_score: int
    lead_id: Optional[int] = None

    def __hash__(self):
        return hash(self.marker_id)


class ClusterEngine:
    """
    Grid-based spatial clustering engine with zoom resolution scaling.
    """
    # Zoom-to-grid size mapping in decimal degrees (lat/lon)
    GRID_SIZES: Dict[int, float] = {
        1: 20.0,
        2: 10.0,
        3: 5.0,
        4: 2.5,
        5: 1.25,
        6: 0.6,
        7: 0.3,
        8: 0.15,
        9: 0.08,
        10: 0.04,
        11: 0.02,
        12: 0.01,
        13: 0.005,
        14: 0.002,
        15: 0.0008,
    }

    @staticmethod
    def get_grid_size(zoom_level: int) -> float:
        """Returns coordinate grid resolution for given zoom level (1 to 19)."""
        z = max(1, min(19, zoom_level))
        if z in ClusterEngine.GRID_SIZES:
            return ClusterEngine.GRID_SIZES[z]
        # For zoom levels >= 16, no clustering (0.0 resolution)
        return 0.0

    @classmethod
    def cluster_points(cls, points: List[Point], zoom_level: int) -> List[MapMarker]:
        """
        Clusters points within viewport for given zoom level.
        Returns list of renderable MapMarker objects.
        """
        if not points:
            return []

        grid_size = cls.get_grid_size(zoom_level)

        # If zoom level is high enough (zoom >= 15) or grid_size is 0, render individual markers directly
        if grid_size == 0.0 or zoom_level >= 15:
            markers: List[MapMarker] = []
            for p in points:
                data = p.data
                lead_id = data.get("id")
                score = data.get("opportunity_score", 0)
                priority = data.get("priority", "Low")
                name = data.get("business_name", "Lead")

                color = cls._get_priority_color(priority)
                marker_id = f"lead_{lead_id}" if lead_id else f"pt_{p.lat:.5f}_{p.lon:.5f}"

                markers.append(
                    MapMarker(
                        marker_id=marker_id,
                        lat=p.lat,
                        lon=p.lon,
                        is_cluster=False,
                        count=1,
                        text=f"{name} (Score: {score})",
                        color=color,
                        opportunity_score=score,
                        lead_id=lead_id
                    )
                )
            return markers

        # Otherwise perform spatial grid aggregation
        clusters: Dict[tuple, List[Point]] = {}

        for p in points:
            grid_x = math.floor(p.lon / grid_size)
            grid_y = math.floor(p.lat / grid_size)
            cell_key = (grid_x, grid_y)
            if cell_key not in clusters:
                clusters[cell_key] = []
            clusters[cell_key].append(p)

        result_markers: List[MapMarker] = []

        for cell_key, cell_points in clusters.items():
            if len(cell_points) == 1:
                p = cell_points[0]
                data = p.data
                lead_id = data.get("id")
                score = data.get("opportunity_score", 0)
                priority = data.get("priority", "Low")
                name = data.get("business_name", "Lead")
                color = cls._get_priority_color(priority)
                marker_id = f"lead_{lead_id}" if lead_id else f"pt_{p.lat:.5f}_{p.lon:.5f}"

                result_markers.append(
                    MapMarker(
                        marker_id=marker_id,
                        lat=p.lat,
                        lon=p.lon,
                        is_cluster=False,
                        count=1,
                        text=f"{name} (Score: {score})",
                        color=color,
                        opportunity_score=score,
                        lead_id=lead_id
                    )
                )
            else:
                # Calculate weighted centroid and max priority score
                total_lat = sum(pt.lat for pt in cell_points)
                total_lon = sum(pt.lon for pt in cell_points)
                count = len(cell_points)
                avg_lat = total_lat / count
                avg_lon = total_lon / count

                max_score = max(pt.data.get("opportunity_score", 0) for pt in cell_points)
                has_high = any(pt.data.get("priority") == "High Opportunity" for pt in cell_points)
                has_med = any(pt.data.get("priority") == "Medium" for pt in cell_points)

                if has_high:
                    color = "#FF4B4B"  # High Opportunity Red
                elif has_med:
                    color = "#FFD166"  # Medium Opportunity Amber
                else:
                    color = "#118AB2"  # Low Opportunity Blue

                marker_id = f"cluster_z{zoom_level}_{cell_key[0]}_{cell_key[1]}"

                result_markers.append(
                    MapMarker(
                        marker_id=marker_id,
                        lat=avg_lat,
                        lon=avg_lon,
                        is_cluster=True,
                        count=count,
                        text=f"Cluster ({count} Leads)",
                        color=color,
                        opportunity_score=max_score,
                        lead_id=None
                    )
                )

        return result_markers

    @staticmethod
    def _get_priority_color(priority: str) -> str:
        """Maps lead priority to UI color code."""
        if priority == "High Opportunity":
            return "#FF4B4B"
        elif priority == "Medium":
            return "#FFD166"
        return "#118AB2"
