"""
Animation & Inertial Physics Engine for LeadForge AI GIS Engine.
Provides cubic/quartic easing curves, spring physics, exponential friction decay for momentum panning,
and smooth camera interpolation targeting 120 FPS.
"""

import time
import math
from typing import Tuple, Optional, Callable


class Easing:
    """Easing functions for fluid UI motion."""
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease out curve: fast start, soft deceleration."""
        return 1.0 - math.pow(1.0 - max(0.0, min(1.0, t)), 3)

    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease out curve: aggressive deceleration."""
        return 1.0 - math.pow(1.0 - max(0.0, min(1.0, t)), 4)

    @staticmethod
    def spring_step(current: float, target: float, velocity: float, stiffness: float = 180.0, damping: float = 18.0, dt: float = 0.0083) -> Tuple[float, float]:
        """Spring physics step calculation."""
        force = -stiffness * (current - target)
        damping_force = -damping * velocity
        accel = force + damping_force
        new_velocity = velocity + accel * dt
        new_position = current + new_velocity * dt
        return new_position, new_velocity


class InertialPhysics:
    """
    Tracks drag velocity vectors (Vx, Vy) and applies exponential friction decay (0.92)
    for Google Maps / Figma style momentum scrolling.
    """
    def __init__(self, friction: float = 0.92, min_velocity: float = 0.05):
        self.friction = friction
        self.min_velocity = min_velocity
        self.vel_x: float = 0.0
        self.vel_y: float = 0.0
        self.last_time: float = 0.0
        self.last_x: float = 0.0
        self.last_y: float = 0.0

    def start_drag(self, x: float, y: float) -> None:
        """Called when user presses mouse button to initiate drag."""
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.last_x = x
        self.last_y = y
        self.last_time = time.perf_counter()

    def update_drag(self, x: float, y: float) -> None:
        """Called during mouse move to calculate instantaneous velocity vector."""
        now = time.perf_counter()
        dt = max(0.001, now - self.last_time)
        self.vel_x = (x - self.last_x) / dt
        self.vel_y = (y - self.last_y) / dt
        self.last_x = x
        self.last_y = y
        self.last_time = now

    def step(self, dt: float = 0.0083) -> Tuple[float, float, bool]:
        """
        Calculates 1 step of momentum decay.
        Returns (dx, dy, is_active).
        """
        if abs(self.vel_x) < self.min_velocity and abs(self.vel_y) < self.min_velocity:
            self.vel_x = 0.0
            self.vel_y = 0.0
            return 0.0, 0.0, False

        dx = self.vel_x * dt
        dy = self.vel_y * dt

        self.vel_x *= self.friction
        self.vel_y *= self.friction

        return dx, dy, True


class CameraAnimator:
    """
    Smoothly interpolates camera position (lat, lon) and zoom level over time.
    """
    def __init__(self):
        self.start_lat: float = 0.0
        self.start_lon: float = 0.0
        self.target_lat: float = 0.0
        self.target_lon: float = 0.0
        self.duration_sec: float = 0.35
        self.elapsed_sec: float = 0.0
        self.is_animating: bool = False

    def animate_to(self, from_lat: float, from_lon: float, to_lat: float, to_lon: float, duration_sec: float = 0.35) -> None:
        """Initiates a smooth camera movement animation."""
        self.start_lat = from_lat
        self.start_lon = from_lon
        self.target_lat = to_lat
        self.target_lon = to_lon
        self.duration_sec = max(0.05, duration_sec)
        self.elapsed_sec = 0.0
        self.is_animating = True

    def update(self, dt: float) -> Tuple[float, float, bool]:
        """
        Advances animation frame by dt seconds.
        Returns (curr_lat, curr_lon, is_active).
        """
        if not self.is_animating:
            return self.target_lat, self.target_lon, False

        self.elapsed_sec += dt
        t = min(1.0, self.elapsed_sec / self.duration_sec)
        eased_t = Easing.ease_out_quart(t)

        curr_lat = self.start_lat + (self.target_lat - self.start_lat) * eased_t
        curr_lon = self.start_lon + (self.target_lon - self.start_lon) * eased_t

        if t >= 1.0:
            self.is_animating = False

        return curr_lat, curr_lon, self.is_animating
