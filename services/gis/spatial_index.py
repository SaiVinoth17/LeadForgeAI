"""
High-Performance 2D QuadTree Spatial Index for LeadForge AI GIS Engine.
Provides O(log N) bounding box spatial queries for 50,000+ coordinates.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    """Represents a spatial point with latitude, longitude, and payload data."""
    lat: float
    lon: float
    data: Dict[str, Any]


class BoundingBox:
    """Represents a 2D spatial geographic bounding box."""
    __slots__ = ("min_lat", "max_lat", "min_lon", "max_lon")

    def __init__(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon

    def contains(self, point: Point) -> bool:
        """Checks if a point lies within the bounding box."""
        return (
            self.min_lat <= point.lat <= self.max_lat and
            self.min_lon <= point.lon <= self.max_lon
        )

    def intersects(self, other: "BoundingBox") -> bool:
        """Checks if this bounding box overlaps with another bounding box."""
        return not (
            other.min_lat > self.max_lat or
            other.max_lat < self.min_lat or
            other.min_lon > self.max_lon or
            other.max_lon < self.min_lon
        )


class QuadTreeNode:
    """Internal QuadTree node for spatial space partitioning."""
    __slots__ = ("boundary", "capacity", "points", "subdivided", "nw", "ne", "sw", "se")

    def __init__(self, boundary: BoundingBox, capacity: int = 32):
        self.boundary = boundary
        self.capacity = capacity
        self.points: List[Point] = []
        self.subdivided: bool = False
        self.nw: Optional["QuadTreeNode"] = None
        self.ne: Optional["QuadTreeNode"] = None
        self.sw: Optional["QuadTreeNode"] = None
        self.se: Optional["QuadTreeNode"] = None

    def subdivide(self) -> None:
        """Subdivides current node into 4 quadrant sub-nodes."""
        mid_lat = (self.boundary.min_lat + self.boundary.max_lat) / 2.0
        mid_lon = (self.boundary.min_lon + self.boundary.max_lon) / 2.0

        # Northwest: upper lat, left lon
        self.nw = QuadTreeNode(BoundingBox(mid_lat, self.boundary.max_lat, self.boundary.min_lon, mid_lon), self.capacity)
        # Northeast: upper lat, right lon
        self.ne = QuadTreeNode(BoundingBox(mid_lat, self.boundary.max_lat, mid_lon, self.boundary.max_lon), self.capacity)
        # Southwest: lower lat, left lon
        self.sw = QuadTreeNode(BoundingBox(self.boundary.min_lat, mid_lat, self.boundary.min_lon, mid_lon), self.capacity)
        # Southeast: lower lat, right lon
        self.se = QuadTreeNode(BoundingBox(self.boundary.min_lat, mid_lat, mid_lon, self.boundary.max_lon), self.capacity)

        self.subdivided = True

    def insert(self, point: Point) -> bool:
        """Inserts a point into the QuadTree node hierarchy."""
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity and not self.subdivided:
            self.points.append(point)
            return True

        if not self.subdivided:
            self.subdivide()
            # Move existing points to children
            existing_points = self.points
            self.points = []
            for p in existing_points:
                self._insert_children(p)

        return self._insert_children(point)

    def _insert_children(self, point: Point) -> bool:
        """Helper method to insert point into appropriate child quadrant."""
        if self.nw and self.nw.insert(point):
            return True
        if self.ne and self.ne.insert(point):
            return True
        if self.sw and self.sw.insert(point):
            return True
        if self.se and self.se.insert(point):
            return True
        return False

    def query_range(self, range_box: BoundingBox, found: List[Point]) -> None:
        """Populates found list with points that intersect range_box."""
        if not self.boundary.intersects(range_box):
            return

        for p in self.points:
            if range_box.contains(p):
                found.append(p)

        if self.subdivided:
            if self.nw:
                self.nw.query_range(range_box, found)
            if self.ne:
                self.ne.query_range(range_box, found)
            if self.sw:
                self.sw.query_range(range_box, found)
            if self.se:
                self.se.query_range(range_box, found)


class QuadTree:
    """
    Root 2D QuadTree spatial index manager.
    """
    def __init__(self, boundary: Optional[BoundingBox] = None, capacity: int = 32):
        if boundary is None:
            # Global geographic bounds
            boundary = BoundingBox(-90.0, 90.0, -180.0, 180.0)
        self.boundary = boundary
        self.capacity = capacity
        self.root = QuadTreeNode(self.boundary, self.capacity)
        self.count = 0

    def insert(self, lat: float, lon: float, data: Dict[str, Any]) -> bool:
        """Inserts a coordinate point into the spatial tree."""
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            return False
        point = Point(lat=lat, lon=lon, data=data)
        success = self.root.insert(point)
        if success:
            self.count += 1
        return success

    def query_range(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[Point]:
        """Performs fast spatial range query returning points within bounding box."""
        found: List[Point] = []
        range_box = BoundingBox(min_lat, max_lat, min_lon, max_lon)
        self.root.query_range(range_box, found)
        return found

    def clear(self) -> None:
        """Clears the spatial index."""
        self.root = QuadTreeNode(self.boundary, self.capacity)
        self.count = 0
