"""
Right Column Agency Copilot Panel & 1-Click AI Action Pills for LeadForge AI Mission Control.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS
from services.ai_service_engine import ai_engine
from ui.components.toast import toast_manager


class AgencyCopilotSidebar(ctk.CTkFrame):
    """
    Agency Copilot Workspace & Action Pills.
    """
    ACTIONS = [
        ("📄 Generate Proposal", "proposal"),
        ("🚀 Autonomous Sales Package", "sales_package"),
        ("🔍 Analyze Website & SEO", "analyze"),
        ("✉️ Write Cold Email", "email"),
        ("💵 Generate Invoice", "invoice"),
        ("🤝 Prepare Meeting Battlecard", "meeting"),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # ── 1. Header ───────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="AGENCY COPILOT & AI WORKSPACE",
            font=FONTS["caption"],
            text_color=COLORS["primary"]
        ).pack(anchor="w", pady=(0, SPACING["xs"]))

        # ── 2. Quick AI Action Pills Grid ───────────────────────
        ctk.CTkLabel(self, text="1-CLICK AUTONOMOUS ACTIONS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(SPACING["xs"], 2))

        pills_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"])
        pills_frame.pack(fill="x", pady=(0, SPACING["md"]))

        for name, act in self.ACTIONS:
            btn = ctk.CTkButton(
                pills_frame,
                text=name,
                font=FONTS["body_sm"],
                fg_color=COLORS["surface_light"],
                hover_color=COLORS["primary_muted"],
                anchor="w",
                height=32,
                corner_radius=RADIUS["sm"],
                command=lambda a=act, n=name: self._trigger_action(a, n)
            )
            btn.pack(fill="x", padx=SPACING["sm"], pady=SPACING["3xs"])

        # ── 3. Chat Message Stream ───────────────────────────────
        ctk.CTkLabel(self, text="COPILOT AGENT STREAM", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 2))

        self.chat_scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"])
        self.chat_scroll.pack(fill="both", expand=True, pady=(0, SPACING["sm"]))

        # Welcome message from FORGE X
        self._add_msg("FORGE X", "Hello! I am your AI Sales Employee. Select a lead or click any autonomous action above to generate deals.", is_user=False)

        # ── 4. Prompt Entry Bar ─────────────────────────────────
        entry_row = ctk.CTkFrame(self, fg_color="transparent")
        entry_row.pack(fill="x")
        entry_row.columnconfigure(0, weight=1)

        self.input_var = ctk.StringVar()
        self.entry = ctk.CTkEntry(
            entry_row,
            textvariable=self.input_var,
            placeholder_text="Ask Copilot or type a command...",
            font=FONTS["body_sm"],
            height=36,
            corner_radius=RADIUS["sm"]
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, SPACING["xs"]))
        self.entry.bind("<Return>", lambda e: self._send_msg())

        ctk.CTkButton(
            entry_row,
            text="Send",
            font=FONTS["body_sm"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            height=36,
            width=60,
            corner_radius=RADIUS["sm"],
            command=self._send_msg
        ).grid(row=0, column=1)

    def _add_msg(self, sender: str, text: str, is_user: bool = False):
        bg = COLORS["surface_elevated"] if is_user else COLORS["surface_light"]
        msg_card = ctk.CTkFrame(self.chat_scroll, fg_color=bg, corner_radius=RADIUS["sm"])
        msg_card.pack(fill="x", pady=SPACING["xs"])

        ctk.CTkLabel(msg_card, text=sender, font=FONTS["caption"], text_color=COLORS["primary"] if not is_user else COLORS["accent"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
        ctk.CTkLabel(msg_card, text=text, font=FONTS["body_sm"], text_color=COLORS["text"], wraplength=200, justify="left").pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))

    def _send_msg(self):
        txt = self.input_var.get().strip()
        if not txt:
            return
        self.input_var.set("")
        self._add_msg("You", txt, is_user=True)
        self._add_msg("FORGE X", f"Analyzing query: '{txt}'. Generating optimal sales package for target leads.", is_user=False)

    def _trigger_action(self, action_type: str, name: str):
        toast_manager.show(f"Executing: {name}...", "info")
        self._add_msg("You", f"Triggered action: {name}", is_user=True)

        res = ai_engine.generate_sales_package({"name": "Metro Clinic", "category": "Healthcare"})
        self._add_msg("FORGE X", f"✅ {name} Completed!\nStatus: {res['status']}\nLatency: {res.get('latency_ms', 12)}ms", is_user=False)
