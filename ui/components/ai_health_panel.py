"""
AI Provider Health & Latency Monitor for LeadForge AI Mission Control.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class AIHealthPanel(ctk.CTkFrame):
    """
    AI Health Monitor Widget.
    """
    PROVIDERS = [
        ("⭐ Gemini 1.5 Flash", "12 ms", "Online", COLORS["success"]),
        ("⚡ Groq LPU", "45 ms", "Online", COLORS["success"]),
        ("💻 Ollama (Local)", "Offline", "Standby", COLORS["warning"]),
        ("🌐 OpenRouter", "180 ms", "Online", COLORS["success"]),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"], **kwargs)

        ctk.CTkLabel(
            self,
            text="AI PROVIDER HEALTH & LATENCY",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        for name, lat, status, color in self.PROVIDERS:
            row = ctk.CTkFrame(self, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"])
            row.pack(fill="x", padx=SPACING["md"], pady=SPACING["3xs"])

            ctk.CTkLabel(row, text=name, font=FONTS["body_sm"], text_color=COLORS["text"]).pack(side="left", padx=SPACING["sm"], pady=4)
            ctk.CTkLabel(row, text=f"{status} ({lat})", font=FONTS["badge"], text_color=color).pack(side="right", padx=SPACING["sm"], pady=4)
