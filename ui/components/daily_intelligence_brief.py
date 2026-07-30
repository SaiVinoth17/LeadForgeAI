"""
Left Column Daily Intelligence Brief for LeadForge AI Mission Control.
Includes Revenue Opportunity Hero Glass Card, Smart AI Insights, and Urgent Action Items.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import get_all_leads


class DailyIntelligenceBrief(ctk.CTkFrame):
    """
    Daily Intelligence Brief Component.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ── 1. Revenue Opportunity Hero Card ────────────────────
        hero_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["primary"]
        )
        hero_card.pack(fill="x", pady=(0, SPACING["md"]))

        ctk.CTkLabel(
            hero_card,
            text="TODAY'S REVENUE OPPORTUNITY",
            font=FONTS["caption"],
            text_color=COLORS["primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], 2))

        self.rev_lbl = ctk.CTkLabel(
            hero_card,
            text="$14,500 USD",
            font=FONTS["metric"],
            text_color=COLORS["text"]
        )
        self.rev_lbl.pack(anchor="w", padx=SPACING["md"])

        ctk.CTkLabel(
            hero_card,
            text="▲ +18.4% vs last week • 4 High-Opportunity deals ready",
            font=FONTS["badge"],
            text_color=COLORS["success"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # ── 2. AI Smart Insights Feed ───────────────────────────
        ctk.CTkLabel(self, text="AI SMART INSIGHTS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(SPACING["xs"], 2))

        insights_box = ctk.CTkScrollableFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], height=220)
        insights_box.pack(fill="both", expand=True, pady=(0, SPACING["md"]))

        insights = [
            ("⭐ HIGHEST PROBABILITY DEAL", "Apex Dental Clinic — 94% opportunity score. Proposal ready."),
            ("📱 MOBILE RESPONSIVENESS ISSUE", "3 Local Hotels have slow mobile loading & broken layouts."),
            ("🔒 SECURITY & SSL DEFICIENCY", "2 Medical Clinics missing SSL certificates."),
            ("🎯 SEO OPPORTUNITY", "5 Restaurants ranked on Page 3 of Google Maps.")
        ]

        for title, desc in insights:
            card = ctk.CTkFrame(insights_box, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"])
            card.pack(fill="x", pady=SPACING["xs"])

            ctk.CTkLabel(card, text=title, font=FONTS["caption"], text_color=COLORS["accent"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
            ctk.CTkLabel(card, text=desc, font=FONTS["body_sm"], text_color=COLORS["text_secondary"], wraplength=220, justify="left").pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))

        # ── 3. Tasks Requiring Attention ───────────────────────
        ctk.CTkLabel(self, text="ACTION ITEMS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 2))
        tasks_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["md"])
        tasks_frame.pack(fill="x")

        items = [
            "• Send Follow-up to Horizon Law",
            "• Approve Deposit Invoice INV-0104",
            "• Review Website Audit for Metro Spa"
        ]
        for item in items:
            ctk.CTkLabel(tasks_frame, text=item, font=FONTS["body_sm"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=SPACING["md"], pady=SPACING["xs"])
