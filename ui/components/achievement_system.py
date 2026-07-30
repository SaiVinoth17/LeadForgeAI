"""
Agency Milestone Achievement System for LeadForge AI Mission Control.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class AchievementSystem(ctk.CTkFrame):
    """
    Gamified Agency Milestone Badges.
    """
    BADGES = [
        ("🏆 100 Businesses Analyzed", "Unlocked"),
        ("💼 First Proposal Won", "Unlocked"),
        ("🚀 ₹10L Pipeline Reached", "Unlocked"),
        ("⚡ 500 AI Automations Completed", "84% Complete"),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"], **kwargs)

        ctk.CTkLabel(
            self,
            text="AGENCY MILESTONES & ACHIEVEMENTS",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        for name, status in self.BADGES:
            row = ctk.CTkFrame(self, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"])
            row.pack(fill="x", padx=SPACING["md"], pady=SPACING["3xs"])

            ctk.CTkLabel(row, text=name, font=FONTS["body_sm"], text_color=COLORS["text"]).pack(side="left", padx=SPACING["sm"], pady=4)
            ctk.CTkLabel(row, text=status, font=FONTS["badge"], text_color=COLORS["success"] if "Unlocked" in status else COLORS["primary"]).pack(side="right", padx=SPACING["sm"], pady=4)
