"""
Global Command Palette Modal (Ctrl+K) for LeadForge AI Mission Control.
Provides instant fuzzy search across leads, AI actions, and app navigation.
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional
from core.config import COLORS, FONTS, SPACING, RADIUS
from core.events import event_bus, Events
from database.crud import get_all_leads


class CommandPaletteModal(ctk.CTkToplevel):
    """
    Raycast / Linear style Command Palette Modal.
    """
    COMMANDS = [
        {"icon": "🚀", "title": "Generate 1-Click Sales Package", "type": "action", "action": "sales_package"},
        {"icon": "📄", "title": "Create Web Redesign Proposal", "type": "action", "action": "proposal"},
        {"icon": "🔍", "title": "Analyze Website & SEO Opportunity", "type": "action", "action": "analyze"},
        {"icon": "✉️", "title": "Draft Cold Email & WhatsApp Pitch", "type": "action", "action": "email"},
        {"icon": "📊", "title": "Navigate to Pipeline CRM", "type": "nav", "target": "crm"},
        {"icon": "🗺️", "title": "Navigate to GIS Map View", "type": "nav", "target": "map_view"},
        {"icon": "🤖", "title": "Navigate to Agency Copilot", "type": "nav", "target": "ai_assistant"},
        {"icon": "⚙️", "title": "Navigate to Settings & AI Setup", "type": "nav", "target": "settings"},
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title("LeadForge AI — Command Palette")
        self.geometry("640x420")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["background"])

        self.transient(master)
        self.grab_set()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Search Input Box ────────────────────────────────────
        input_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], height=54, corner_radius=RADIUS["md"])
        input_frame.grid(row=0, column=0, sticky="ew", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))
        input_frame.columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.search_var,
            placeholder_text="Type a command, search leads, or type 'Ctrl+K'...",
            font=FONTS["body"],
            height=40,
            fg_color="transparent",
            border_width=0
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=SPACING["md"])
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # ── Results List Container ──────────────────────────────
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.results_scroll.grid(row=1, column=0, sticky="nsew", padx=SPACING["md"], pady=(0, SPACING["md"]))

        self._render_results("")

    def _on_search(self, event=None):
        query = self.search_var.get().lower()
        self._render_results(query)

    def _render_results(self, query: str):
        for w in self.results_scroll.winfo_children():
            w.destroy()

        # 1. Matching System Commands
        ctk.CTkLabel(self.results_scroll, text="QUICK COMMANDS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 2))

        for cmd in self.COMMANDS:
            if not query or query in cmd["title"].lower():
                btn = ctk.CTkButton(
                    self.results_scroll,
                    text=f"{cmd['icon']}   {cmd['title']}",
                    font=FONTS["body"],
                    fg_color="transparent",
                    hover_color=COLORS["surface_light"],
                    anchor="w",
                    height=36,
                    corner_radius=RADIUS["sm"],
                    command=lambda c=cmd: self._execute_command(c)
                )
                btn.pack(fill="x", pady=1)

        # 2. Matching Leads
        leads = get_all_leads()
        matched_leads = [l for l in leads if query and (query in l.business_name.lower() or (l.category and query in l.category.lower()))][:5]

        if matched_leads:
            ctk.CTkLabel(self.results_scroll, text="PROSPECT LEADS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["md"], 2))
            for l in matched_leads:
                btn = ctk.CTkButton(
                    self.results_scroll,
                    text=f"🏢   {l.business_name} ({l.category or 'Business'}) — Score: {l.opportunity_score or 70}",
                    font=FONTS["body_sm"],
                    fg_color="transparent",
                    hover_color=COLORS["surface_light"],
                    anchor="w",
                    height=34,
                    corner_radius=RADIUS["sm"],
                    command=lambda lead=l: self._select_lead(lead)
                )
                btn.pack(fill="x", pady=1)

    def _execute_command(self, cmd: dict):
        if cmd["type"] == "nav":
            event_bus.emit(Events.NAVIGATE, cmd["target"])
        self._close()

    def _select_lead(self, lead: Any):
        event_bus.emit(Events.NAVIGATE, "proposals")
        self._close()

    def _close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
