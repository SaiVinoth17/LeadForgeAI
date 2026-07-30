"""
Phase 6: Inter-Agent Conversation Feed Component for FORGE OS V5.
Displays real-time inter-process communication between AI agents.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class AgentChatStream(ctk.CTkFrame):
    """
    Simulated Inter-Agent Conversation Feed.
    """
    LOGS = [
        ("🔬 Research Agent", "Indexed 46 local businesses in QuadTree. 8 high-opportunity targets flagged."),
        ("⚡ SEO Agent", "Audited Blue Hills Resort: Mobile score is 41/100. Google Maps ranking is Page 3."),
        ("📄 Proposal Agent", "Pre-generated Enterprise SEO & Local Maps Boost proposal (Est. ₹1.45L)."),
        ("📊 CRM Agent", "Moved Blue Hills Resort to 'Qualified' stage. Next recommended contact: Owner."),
        ("💵 Invoice Agent", "Prepared 50% upfront retainer invoice template INV-0105."),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"], **kwargs)

        # Header
        ctk.CTkLabel(
            self,
            text="AUTONOMOUS AGENT INTER-PROCESS CHAT FEED",
            font=FONTS["caption"],
            text_color=COLORS["primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=150)
        scroll.pack(fill="both", expand=True, padx=SPACING["sm"], pady=(0, SPACING["md"]))

        for agent, text in self.LOGS:
            card = ctk.CTkFrame(scroll, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"])
            card.pack(fill="x", pady=SPACING["3xs"])

            ctk.CTkLabel(card, text=agent, font=FONTS["badge"], text_color=COLORS["accent"]).pack(anchor="w", padx=SPACING["sm"], pady=(2, 0))
            ctk.CTkLabel(card, text=text, font=FONTS["body_sm"], text_color=COLORS["text_secondary"], wraplength=220, justify="left").pack(anchor="w", padx=SPACING["sm"], pady=(0, 2))
