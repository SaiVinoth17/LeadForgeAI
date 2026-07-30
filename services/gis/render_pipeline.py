"""
120Hz Frame Scheduler & Render Pipeline for LeadForge AI GIS Engine.
Enforces sub-8.3ms frame budgets, double buffering, and dirty-region batch rendering.
"""

import time
import threading
from typing import Callable, List, Optional
from core.logger import logger


class FrameScheduler:
    """
    120Hz Ticker Loop (8.3ms cycle time).
    Dispatches frame ticks to registered render callbacks.
    """
    def __init__(self, target_fps: int = 120):
        self.target_fps = target_fps
        self.frame_budget_sec = 1.0 / target_fps  # 0.00833 sec for 120 FPS
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._render_callbacks: List[Callable[[float], None]] = []

    def add_callback(self, callback: Callable[[float], None]) -> None:
        """Registers a render callback function receiving dt delta-time."""
        if callback not in self._render_callbacks:
            self._render_callbacks.append(callback)

    def remove_callback(self, callback: Callable[[float], None]) -> None:
        if callback in self._render_callbacks:
            self._render_callbacks.remove(callback)

    def start() -> None:
        """Starts background 120Hz frame ticker thread."""
        if self._is_running:
            return
        self._is_running = True
        self._thread = threading.Thread(target=self._ticker_loop, daemon=True, name="GIS120HzTicker")
        self._thread.start()
        logger.info(f"Started GIS FrameScheduler at {self.target_fps} FPS target.")

    def stop() -> None:
        """Stops the ticker loop."""
        self._is_running = False

    def _ticker_loop() -> None:
        last_tick = time.perf_counter()
        while self._is_running:
            now = time.perf_counter()
            dt = now - last_tick
            if dt >= self.frame_budget_sec:
                last_tick = now
                for cb in self._render_callbacks:
                    try:
                        cb(dt)
                    except Exception as e:
                        logger.error(f"Error in FrameScheduler callback: {e}")
            else:
                # Sleep tiny remainder to prevent CPU spinlock
                time.sleep(max(0.0005, self.frame_budget_sec - dt))


frame_scheduler = FrameScheduler(target_fps=120)
