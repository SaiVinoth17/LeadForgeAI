"""
Bottom Live Scrolling Automation Timeline for LeadForge AI Mission Control.
Displays real-time event ticker of all automated AI executions.
"""

import time
import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class LiveAutomationTimeline(ctk.CTkFrame):
    """
    Bottom Live Event Timeline Ticker Widget.
    """
    EVENTS = [
        ("09:31", "🔍 Website Analyzed", "Apex Dental Clinic — Score: 94/100"),
        ("09:32", "📄 Proposal Generated", "Enterprise Next.js Redesign ($2.8k)"),
        ("09:33", "✉️ Cold Email Written", "Personalized performance pitch sent to draft"),
        ("09:34", "💬 WhatsApp Pitch Drafted", "3-sentence audio script prepared"),
        ("09:35", "💵 Invoice Created", "50% Upfront Retainer INV-0104 ($1.4k)"),
        ("09:36", "📊 CRM Synced", "Opportunity moved to 'Qualified' stage")
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"], **kwargs)

        self.pack_propagate(False)

        # Header bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], 2))

        ctk.CTkLabel(top_bar, text="LIVE AUTONOMOUS EXECUTION TIMELINE", font=FONTS["caption"], text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkLabel(top_bar, text="● LIVE TICKER", font=FONTS["badge"], text_color=COLORS["success"]).pack(side="right")

        # Horizontal Scroll Container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", orientation="horizontal", height=50)
        self.scroll_frame.pack(fill="both", expand=True, padx=SPACING["sm"], pady=(0, SPACING["xs"]))

        for timestamp, action, detail in self.EVENTS:
            card = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"], border_width=1, border_color=COLORS["border"])
            card.pack(side="left", padx=SPACING["xs"], pady=2)

            t_box = ctk.CTkFrame(card, fg_color="transparent")
            t_box.pack(fill="x", padx=SPACING["sm"], pady=(2, 0))

            ctk.CTkLabel(t_box, text=timestamp, font=FONTS["badge"], text_color=COLORS["text_muted"]).pack(side="left")
            ctk.CTkLabel(t_box, text=action, font=FONTS["caption"], text_color=COLORS["text"]).pack(side="left", padx=(SPACING["xs"], 0))

            ctk.CTkLabel(card, text=detail, font=FONTS["body_sm"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=SPACING["sm"], pady=(0, 2))
