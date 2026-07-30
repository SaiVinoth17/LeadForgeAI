"""
Phase 5: Opportunity Matrix Component for FORGE OS V5.
4-Quadrant visual matrix categorizing leads into Easy Win, High Value, Low Value, and Long Term.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import get_all_leads


class OpportunityMatrix(ctk.CTkFrame):
    """
    4-Quadrant Lead Opportunity Matrix.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"], **kwargs)

        # Header
        ctk.CTkLabel(
            self,
            text="OPPORTUNITY CLASSIFICATION MATRIX",
            font=FONTS["caption"],
            text_color=COLORS["primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        # Grid Container
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        grid.columnconfigure((0, 1), weight=1)
        grid.rowconfigure((0, 1), weight=1)

        quadrants = [
            ("⚡ EASY WINS (High Score, Fast Close)", ["Blue Hills Resort (96%)", "Apex Clinic (94%)"], COLORS["success"]),
            ("💎 HIGH VALUE (Big Deals)", ["Grand Horizon Hotel", "Metro Health"], COLORS["primary"]),
            ("⏳ LONG TERM (Nurture)", ["City Cafe", "Prime Dental"], COLORS["warning"]),
            ("🔥 HIGH COMPETITION", ["Summit Spa"], COLORS["accent"]),
        ]

        for idx, (title, items, color) in enumerate(quadrants):
            r, c = divmod(idx, 2)
            card = ctk.CTkFrame(grid, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"], border_width=1, border_color=COLORS["border"])
            card.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

            ctk.CTkLabel(card, text=title, font=FONTS["badge"], text_color=color).pack(anchor="w", padx=SPACING["sm"], pady=(4, 2))
            for item in items:
                ctk.CTkLabel(card, text=f"• {item}", font=FONTS["body_sm"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=SPACING["sm"], pady=1)
