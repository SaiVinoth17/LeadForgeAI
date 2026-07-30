"""
Phase 3: Digital Twin Card Component for FORGE OS V5.
Displays real-time lead Digital Twin metrics (Health, SEO, Performance, Buying Intent, Decision Maker).
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS
from services.memory_engine import memory_engine


class DigitalTwinCard(ctk.CTkFrame):
    """
    Lead Digital Twin Visual Card.
    """
    def __init__(self, master, business_name: str = "Blue Hills Resort", **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["primary"], **kwargs)

        mem = memory_engine.get_client_memory(business_name)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        ctk.CTkLabel(hdr, text="DIGITAL TWIN PROFILE", font=FONTS["caption"], text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkLabel(hdr, text="● SYNCED", font=FONTS["badge"], text_color=COLORS["success"]).pack(side="right")

        ctk.CTkLabel(self, text=business_name, font=FONTS["heading2"], text_color=COLORS["text"]).pack(anchor="w", padx=SPACING["md"])

        # Grid Metrics
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])
        grid.columnconfigure((0, 1), weight=1)

        metrics = [
            ("Overall Health", "87%", COLORS["success"]),
            ("SEO Score", f"{mem['seo_score']}%", COLORS["warning"]),
            ("Performance", f"{mem['performance_score']}%", COLORS["danger"]),
            ("Buying Intent", mem["buying_intent"], COLORS["accent"]),
            ("Decision Maker", mem["decision_maker"], COLORS["text"]),
            ("Win Probability", mem["probability"], COLORS["success"]),
        ]

        for idx, (label, val, color) in enumerate(metrics):
            r, c = divmod(idx, 2)
            box = ctk.CTkFrame(grid, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"])
            box.grid(row=r, column=c, sticky="ew", padx=2, pady=2)

            ctk.CTkLabel(box, text=label, font=FONTS["badge"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["sm"], pady=(2, 0))
            ctk.CTkLabel(box, text=val, font=FONTS["body_sm"], text_color=color).pack(anchor="w", padx=SPACING["sm"], pady=(0, 2))
