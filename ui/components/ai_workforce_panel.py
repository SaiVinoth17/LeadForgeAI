"""
AI Workforce Employee Panel for LeadForge AI Mission Control.
Tracks 8 autonomous AI employees working simultaneously.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class AIWorkforcePanel(ctk.CTkFrame):
    """
    8 Virtual AI Employee Tracker.
    """
    AGENTS = [
        ("🔬 Research Agent", "Active", 0.90, "Indexing spatial QuadTree"),
        ("⚡ SEO Agent", "Active", 0.75, "Auditing 46 business sites"),
        ("📄 Proposal Agent", "Generating", 0.95, "Drafting Apex Dental Proposal"),
        ("✉️ Email Agent", "Active", 0.60, "Writing personalized copy"),
        ("📊 CRM Agent", "Syncing", 0.85, "Updating pipeline stages"),
        ("📈 Analytics Agent", "Idle", 1.00, "Telemetry monitoring"),
        ("📜 Contract Agent", "Idle", 1.00, "Legal template ready"),
        ("💵 Invoice Agent", "Idle", 1.00, "50% retainer milestone ready"),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"], **kwargs)

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        ctk.CTkLabel(hdr, text="AUTONOMOUS AI WORKFORCE (8 EMPLOYEES)", font=FONTS["caption"], text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkLabel(hdr, text="🟢 5 Working • 3 Idle", font=FONTS["badge"], text_color=COLORS["success"]).pack(side="right")

        # Scrollable Agents List
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=160)
        scroll.pack(fill="both", expand=True, padx=SPACING["sm"], pady=(0, SPACING["md"]))

        for name, status, progress, task in self.AGENTS:
            row = ctk.CTkFrame(scroll, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"])
            row.pack(fill="x", pady=SPACING["3xs"])

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x", padx=SPACING["sm"], pady=(2, 0))

            ctk.CTkLabel(top, text=name, font=FONTS["body_sm"], text_color=COLORS["text"]).pack(side="left")
            ctk.CTkLabel(top, text=status, font=FONTS["badge"], text_color=COLORS["success"] if status != "Idle" else COLORS["text_muted"]).pack(side="right")

            pbar = ctk.CTkProgressBar(row, height=4, progress_color=COLORS["primary"] if status != "Idle" else COLORS["surface_elevated"])
            pbar.pack(fill="x", padx=SPACING["sm"], pady=2)
            pbar.set(progress)

            ctk.CTkLabel(row, text=task, font=FONTS["badge"], text_color=COLORS["text_tertiary"]).pack(anchor="w", padx=SPACING["sm"], pady=(0, 2))
