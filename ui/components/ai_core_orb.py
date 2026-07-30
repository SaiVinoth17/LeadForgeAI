"""
AI CORE Identity Orb Component for LeadForge AI Mission Control.
Provides an animated visual orb identity with dynamic state colors and pulsing effects.
"""

import math
import tkinter as tk
import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class AICoreOrb(ctk.CTkFrame):
    """
    Pulsing AI CORE Orb Widget.
    """
    STATES = {
        "Idle": COLORS["success"],       # Emerald Green
        "Thinking": COLORS["info"],      # Cyan Blue
        "Analyzing": COLORS["accent"],   # Purple Glow
        "Generating": COLORS["primary"], # Indigo Pulse
        "Waiting": COLORS["warning"],    # Amber Warning
        "Error": COLORS["danger"],      # Crimson Red
    }

    def __init__(self, master, initial_state: str = "Idle", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.state_name = initial_state
        self.pulse_phase: float = 0.0

        # Layout
        self.canvas = tk.Canvas(self, width=32, height=32, bg=COLORS["background"], highlightthickness=0)
        self.canvas.pack(side="left", padx=(0, SPACING["xs"]))

        self.label = ctk.CTkLabel(
            self,
            text=f"AI CORE: {self.state_name.upper()}",
            font=FONTS["badge"],
            text_color=self.STATES.get(self.state_name, COLORS["primary"])
        )
        self.label.pack(side="left")

        # Start pulsing animation
        self._animate_orb()

    def set_state(self, new_state: str):
        """Updates AI Core State."""
        if new_state in self.STATES:
            self.state_name = new_state
            self.label.configure(
                text=f"AI CORE: {self.state_name.upper()}",
                text_color=self.STATES[self.state_name]
            )

    def _animate_orb(self):
        def _tick():
            if not self.winfo_exists():
                return

            try:
                self.canvas.delete("all")
                color = self.STATES.get(self.state_name, COLORS["primary"])

                self.pulse_phase += 0.12
                radius = 10 + 3 * math.sin(self.pulse_phase)

                cx, cy = 16, 16
                # Outer glow ring
                self.canvas.create_oval(cx - radius - 2, cy - radius - 2, cx + radius + 2, cy + radius + 2, fill="", outline=color, width=1)
                # Solid inner core
                self.canvas.create_oval(cx - radius + 2, cy - radius + 2, cx + radius - 2, cy + radius - 2, fill=color, outline="")

            except Exception:
                pass

            self.after(50, _tick)

        self.after(50, _tick)
