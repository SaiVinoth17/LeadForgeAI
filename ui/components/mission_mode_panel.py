"""
Agency Mission Mode Command Panel for LeadForge AI Mission Control.
Enables agency owners to set high-level revenue target missions.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class MissionModePanel(ctk.CTkFrame):
    """
    Agency Mission Command Panel Widget.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["accent"], **kwargs)

        # Header
        ctk.CTkLabel(
            self,
            text="🎯 ACTIVE AGENCY MISSION MODE",
            font=FONTS["caption"],
            text_color=COLORS["accent"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], 2))

        ctk.CTkLabel(
            self,
            text="Mission: Acquire 10 Local Hotel Clients",
            font=FONTS["heading3"],
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=SPACING["md"])

        # Progress
        p_frame = ctk.CTkFrame(self, fg_color="transparent")
        p_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        ctk.CTkLabel(p_frame, text="Progress: 6 / 10 Hotels Closed", font=FONTS["body_sm"], text_color=COLORS["success"]).pack(side="left")
        ctk.CTkLabel(p_frame, text="Est. Revenue: ₹12.0 Lakhs", font=FONTS["body_sm"], text_color=COLORS["text_secondary"]).pack(side="right")

        pbar = ctk.CTkProgressBar(self, height=8, progress_color=COLORS["accent"])
        pbar.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))
        pbar.set(0.60)

        # Footer Stats
        ftr = ctk.CTkFrame(self, fg_color="transparent")
        ftr.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

        ctk.CTkLabel(ftr, text="🤖 4 AI Agents Assigned", font=FONTS["badge"], text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkLabel(ftr, text="⏱ ETA: 43 Mins", font=FONTS["badge"], text_color=COLORS["warning"]).pack(side="right")
