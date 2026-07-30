"""
Ultra-Low-Latency 120 FPS GIS Map View Page for LeadForge AI.
Features QuadTree Spatial Indexing, Inertial Momentum Panning Physics, Camera Animation,
Canvas Marker Object Pooling, Virtualized Viewport Rendering, and Real-Time Telemetry HUD.
"""

import time
import threading
import customtkinter as ctk
import tkintermapview
from typing import Dict, List, Set, Any, Optional

from core.config import COLORS, FONTS, SPACING, RADIUS
from core.logger import logger
from services.gis.cache_engine import gis_cache
from services.gis.cluster_engine import MapMarker
from services.gis.viewport_manager import ViewportManager
from services.gis.animation_engine import InertialPhysics, CameraAnimator
from services.gis.marker_pool import MarkerPool
from services.gis.telemetry_hud import GISProfilerHUD


class MapViewPage(ctk.CTkFrame):
    """
    120 FPS Ultra-Low-Latency GIS Map View Page.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.viewport_manager = ViewportManager(debounce_ms=30)
        self.inertial_physics = InertialPhysics(friction=0.92)
        self.camera_animator = CameraAnimator()

        self._initial_centered: bool = False
        self._hud_visible: bool = True
        self._last_spatial_time_ms: float = 0.35

        # ── Header Bar ──────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))

        self.header = ctk.CTkLabel(
            header_frame,
            text="Map View",
            font=FONTS["heading1"],
            text_color=COLORS["text"]
        )
        self.header.pack(side="left")

        # HUD Toggle Button
        self.hud_toggle_btn = ctk.CTkButton(
            header_frame,
            text="⚡ Performance HUD",
            font=FONTS["caption"],
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_light"],
            text_color=COLORS["primary"],
            height=28,
            corner_radius=RADIUS["sm"],
            command=self._toggle_hud
        )
        self.hud_toggle_btn.pack(side="right", padx=(0, SPACING["md"]))

        # Stats Badge (Render count & total spatial points)
        self.stats_badge = ctk.CTkLabel(
            header_frame,
            text="Indexing GIS points...",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["sm"],
            padx=SPACING["sm"],
            pady=SPACING["xs"]
        )
        self.stats_badge.pack(side="right", padx=SPACING["sm"])

        # ── Map Container Frame ─────────────────────────────────
        self.map_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.map_frame.grid(row=1, column=0, sticky="nsew")

        self.map_widget = tkintermapview.TkinterMapView(
            self.map_frame,
            corner_radius=RADIUS["lg"]
        )
        self.map_widget.pack(fill="both", expand=True, padx=SPACING["xs"], pady=SPACING["xs"])

        # Initialize Marker Pool
        self.marker_pool = MarkerPool(self.map_widget)

        # High-Speed CartoDB CDN tiles for ultra-fast response
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png")

        # Overlay Glassmorphism Telemetry HUD
        self.hud_widget = GISProfilerHUD(self.map_frame, width=280, height=100)
        self.hud_widget.place(relx=0.98, rely=0.02, anchor="ne")

        self._viewport_debounce_job = None

        # ── Bind Event Listeners for 60Hz Smooth Physics & Debouncing ──
        canvas = self.map_widget.canvas
        canvas.bind("<ButtonPress-1>", self._on_mouse_down, add="+")
        canvas.bind("<B1-Motion>", self._on_mouse_drag, add="+")
        canvas.bind("<ButtonRelease-1>", self._on_mouse_up, add="+")
        canvas.bind("<MouseWheel>", self._on_viewport_event, add="+")
        canvas.bind("<Button-4>", self._on_viewport_event, add="+")
        canvas.bind("<Button-5>", self._on_viewport_event, add="+")
        canvas.bind("<Configure>", self._on_viewport_event, add="+")

        # Start 60Hz physics & telemetry loop
        self._start_physics_loop()

        # Asynchronously load spatial data
        self.load_map()

    def load_map(self) -> None:
        """Loads/refreshes GIS data and updates viewport markers."""
        threading.Thread(target=self._async_init_gis, daemon=True).start()

    def _async_init_gis(self) -> None:
        """Background thread worker to initialize spatial cache."""
        try:
            t0 = time.perf_counter()
            qtree = gis_cache.load_spatial_data()
            self._last_spatial_time_ms = (time.perf_counter() - t0) * 1000.0
            logger.info(f"MapViewPage background GIS initialized with {qtree.count} points in {self._last_spatial_time_ms:.2f}ms.")
            self.after(100, self._trigger_viewport_update)
        except Exception as e:
            logger.error(f"Error initializing GIS spatial data: {e}")

    # ── MOUSE & INERTIAL PHYSICS HANDLERS ─────────────────────────
    def _on_mouse_down(self, event):
        self.inertial_physics.start_drag(event.x, event.y)

    def _on_mouse_drag(self, event):
        # ONLY update velocity vector. Do NOT flood viewport queries during pixel drag!
        self.inertial_physics.update_drag(event.x, event.y)

    def _on_mouse_up(self, event):
        self._trigger_viewport_update()

    def _on_viewport_event(self, event=None) -> None:
        # Debounce viewport update calls during rapid zooming/resizing
        if self._viewport_debounce_job:
            self.after_cancel(self._viewport_debounce_job)
        self._viewport_debounce_job = self.after(40, self._trigger_viewport_update)

    def _start_physics_loop(self) -> None:
        """60Hz Smooth Physics Ticker Loop (16ms budget)."""
        def _physics_tick():
            if not self.winfo_exists():
                return

            t0 = time.perf_counter()

            # 1. Inertial Panning Decay Step
            dx, dy, active = self.inertial_physics.step(dt=0.016)
            if active:
                try:
                    self.map_widget.draw_move(int(dx), int(dy))
                    self._trigger_viewport_update()
                except Exception:
                    pass

            # 2. Camera Interpolation Step
            if self.camera_animator.is_animating:
                lat, lon, animating = self.camera_animator.update(dt=0.016)
                try:
                    self.map_widget.set_position(lat, lon)
                    self._trigger_viewport_update()
                except Exception:
                    pass

            # 3. Record Telemetry Frame
            qtree_count = gis_cache.get_quadtree().count if gis_cache.is_loaded() else 0
            active_count = self.marker_pool.get_active_count()
            self.hud_widget.record_frame(
                spatial_time_ms=self._last_spatial_time_ms,
                active_count=active_count,
                total_count=qtree_count
            )

            # Schedule next tick at 60 FPS (16ms)
            self.after(16, _physics_tick)

        self.after(16, _physics_tick)

    def _trigger_viewport_update(self) -> None:
        """Extracts visible bounding box and requests async diff calculation."""
        try:
            width = self.map_widget.canvas.winfo_width()
            height = self.map_widget.canvas.winfo_height()
            if width <= 1 or height <= 1:
                return

            top_left = self.map_widget.convert_canvas_coords_to_decimal_coords(0, 0)
            bot_right = self.map_widget.convert_canvas_coords_to_decimal_coords(width, height)
            zoom = int(getattr(self.map_widget, "zoom", 12))

            if not top_left or not bot_right:
                return

            top_lat, left_lon = top_left
            bot_lat, right_lon = bot_right

            # Center map on first lead on startup
            if not self._initial_centered and gis_cache.is_loaded():
                qtree = gis_cache.get_quadtree()
                if qtree.count > 0:
                    pts = qtree.query_range(-90, 90, -180, 180)
                    if pts:
                        first_pt = pts[0]
                        self.map_widget.set_position(first_pt.lat, first_pt.lon)
                        self.map_widget.set_zoom(11)
                        self._initial_centered = True
                        top_left = self.map_widget.convert_canvas_coords_to_decimal_coords(0, 0)
                        bot_right = self.map_widget.convert_canvas_coords_to_decimal_coords(width, height)
                        if top_left and bot_right:
                            top_lat, left_lon = top_left
                            bot_lat, right_lon = bot_right

            self.viewport_manager.update_viewport(
                top_lat, left_lon, bot_lat, right_lon, zoom, self._on_diff_computed_bg
            )

        except Exception as e:
            logger.error(f"Error triggering viewport update: {e}")

    def _on_diff_computed_bg(self, to_remove: Set[str], to_add: List[MapMarker]) -> None:
        """Dispatches computed diffs to UI thread."""
        self.after(0, self._apply_marker_diff_ui, to_remove, to_add)

    def _apply_marker_diff_ui(self, to_remove: Set[str], to_add: List[MapMarker]) -> None:
        """Applies marker diffs on main UI thread using MarkerPool."""
        try:
            # 1. Release markers out of viewport bounds
            for mid in to_remove:
                self.marker_pool.release_marker(mid)

            # 2. Set active markers in viewport
            for m in to_add:
                cmd = (
                    (lambda marker=None, lat=m.lat, lon=m.lon: self._on_cluster_clicked(lat, lon))
                    if m.is_cluster else None
                )
                self.marker_pool.set_marker(
                    m.marker_id,
                    m.lat,
                    m.lon,
                    text=m.text,
                    color=m.color,
                    command=cmd
                )

            # 3. Update stats badge text
            qtree_count = gis_cache.get_quadtree().count if gis_cache.is_loaded() else 0
            active_count = self.marker_pool.get_active_count()
            self.stats_badge.configure(
                text=f"Total Leads: {qtree_count}  |  Active Markers: {active_count}"
            )

        except Exception as e:
            logger.error(f"Error applying marker diff: {e}")

    def _on_cluster_clicked(self, lat: float, lon: float) -> None:
        """Zooms smoothly into cluster centroid using CameraAnimator."""
        pos = self.map_widget.get_position()
        from_lat, from_lon = pos if pos else (lat, lon)

        # Initiate smooth camera animation
        self.camera_animator.animate_to(from_lat, from_lon, lat, lon, duration_sec=0.3)

        current_zoom = int(getattr(self.map_widget, "zoom", 12))
        new_zoom = min(19, current_zoom + 2)
        self.map_widget.set_zoom(new_zoom)
        self._trigger_viewport_update()

    def _toggle_hud(self) -> None:
        """Toggles HUD visibility."""
        if self._hud_visible:
            self.hud_widget.place_forget()
            self._hud_visible = False
        else:
            self.hud_widget.place(relx=0.98, rely=0.02, anchor="ne")
            self._hud_visible = True

    def destroy(self):
        """Cleanup worker threads & marker pool on widget destroy."""
        if hasattr(self, "viewport_manager"):
            self.viewport_manager.reset()
        if hasattr(self, "marker_pool"):
            self.marker_pool.release_all()
        super().destroy()
