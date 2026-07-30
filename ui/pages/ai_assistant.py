"""
Agency Copilot Page for LeadForge AI.
Features a 3-pane enterprise workspace: Session & Prompt Library, Intelligence Chat Stream
with Quick Action Pills, and Live Business Context Inspector.
"""

import customtkinter as ctk
import threading
from typing import Dict, List, Optional, Any

from core.config import COLORS, FONTS, SPACING, RADIUS
from core.logger import logger
from database.crud import get_all_leads, update_lead
from core.forge_os.planner import planner
from services.ai_generators import (
    proposal_gen, email_gen, whatsapp_gen, call_script_gen, meeting_points_gen
)
from ui.components.toast import toast_manager


class AIAssistantPage(ctk.CTkFrame):
    """
    Agency Copilot 3-Pane Page Implementation.
    """
    QUICK_ACTIONS = [
        ("Cold Email", "Generate cold outreach email"),
        ("WhatsApp Pitch", "Generate WhatsApp pitch message"),
        ("Proposal", "Generate custom website proposal"),
        ("Website Audit", "Audit website security and responsiveness"),
        ("SEO Strategy", "Generate local SEO growth strategy"),
        ("Landing Page", "Generate high-converting landing page copy"),
        ("Cost Estimator", "Estimate project value & timeline"),
        ("Sales Package", "Generate full sales outreach package")
    ]

    TEMPLATES = [
        "Cold Email Generator",
        "WhatsApp Pitch Generator",
        "SEO Audit Report",
        "Landing Page Copywriter",
        "Price Objection Handler"
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.leads: List[Any] = []
        self.selected_lead: Optional[Any] = None
        self.chat_history: List[Dict[str, str]] = []

        # ── Page Header ──────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, SPACING["md"]))

        ctk.CTkLabel(
            header_frame,
            text="Agency Copilot",
            font=FONTS["heading1"],
            text_color=COLORS["text"]
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="Autonomous Business Intelligence & Strategy Engine",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=SPACING["md"], pady=(4, 0))

        # ── 3-Pane Grid Container ────────────────────────────────
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        body_frame.columnconfigure(1, weight=1)
        body_frame.rowconfigure(0, weight=1)

        # ── LEFT PANE: Session & Prompt Library ─────────────────
        self.left_pane = ctk.CTkFrame(
            body_frame,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            width=260
        )
        self.left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["md"]))
        self.left_pane.pack_propagate(False)

        self._build_left_pane()

        # ── CENTER PANE: Intelligence Chat Workspace ─────────────
        self.center_pane = ctk.CTkFrame(
            body_frame,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.center_pane.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING["md"]))

        self._build_center_pane()

        # ── RIGHT PANE: Business Context Inspector ──────────────
        self.right_pane = ctk.CTkFrame(
            body_frame,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            width=280
        )
        self.right_pane.grid(row=0, column=2, sticky="nsew")
        self.right_pane.pack_propagate(False)

        self._build_right_pane()

        self.load_leads()
        self._append_system_welcome()

    # ── LEFT PANE BUILDER ───────────────────────────────────────
    def _build_left_pane(self):
        container = ctk.CTkScrollableFrame(self.left_pane, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        # New Session Button
        ctk.CTkButton(
            container,
            text="+ New Session",
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            corner_radius=RADIUS["sm"],
            height=34,
            command=self._new_session
        ).pack(fill="x", pady=(0, SPACING["md"]))

        # Context Selector
        ctk.CTkLabel(container, text="ACTIVE BUSINESS CONTEXT", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, SPACING["xs"]))
        self.context_var = ctk.StringVar(value="Select Prospect...")
        self.context_dropdown = ctk.CTkOptionMenu(
            container,
            values=["Select Prospect..."],
            variable=self.context_var,
            font=FONTS["body_sm"],
            height=30,
            corner_radius=RADIUS["sm"],
            command=self._on_context_selected
        )
        self.context_dropdown.pack(fill="x", pady=(0, SPACING["md"]))

        # History Section
        ctk.CTkLabel(container, text="RECENT SESSIONS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, SPACING["xs"]))
        history_items = ["Daily Briefing", "Dental Outreach Strategy", "Website Redesign Pitch"]
        for h in history_items:
            btn = ctk.CTkButton(
                container, text=f"💬 {h}", font=FONTS["body_sm"], fg_color="transparent",
                text_color=COLORS["text_secondary"], hover_color=COLORS["surface_light"],
                anchor="w", height=28, corner_radius=RADIUS["sm"]
            )
            btn.pack(fill="x", pady=SPACING["3xs"])

        # Pinned Templates Section
        ctk.CTkLabel(container, text="PINNED TEMPLATES", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(SPACING["md"], SPACING["xs"]))
        for t in self.TEMPLATES:
            btn = ctk.CTkButton(
                container, text=f"📌 {t}", font=FONTS["body_sm"], fg_color="transparent",
                text_color=COLORS["text_secondary"], hover_color=COLORS["surface_light"],
                anchor="w", height=28, corner_radius=RADIUS["sm"],
                command=lambda template=t: self._insert_template(template)
            )
            btn.pack(fill="x", pady=SPACING["3xs"])

    # ── CENTER PANE BUILDER ──────────────────────────────────────
    def _build_center_pane(self):
        self.center_pane.rowconfigure(1, weight=1)
        self.center_pane.columnconfigure(0, weight=1)

        # Quick Actions Bar
        actions_bar = ctk.CTkScrollableFrame(self.center_pane, fg_color=COLORS["surface_light"], height=48, orientation="horizontal")
        actions_bar.grid(row=0, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["md"])

        for name, prompt_text in self.QUICK_ACTIONS:
            btn = ctk.CTkButton(
                actions_bar,
                text=name,
                font=FONTS["caption"],
                fg_color=COLORS["surface_elevated"],
                hover_color=COLORS["primary_muted"],
                corner_radius=RADIUS["sm"],
                height=28,
                command=lambda p=prompt_text: self._execute_quick_action(p)
            )
            btn.pack(side="left", padx=SPACING["xs"], pady=SPACING["xs"])

        # Chat Message Stream
        self.chat_scroll = ctk.CTkScrollableFrame(self.center_pane, fg_color="transparent")
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        # Command Input Bar
        input_frame = ctk.CTkFrame(self.center_pane, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=SPACING["md"], pady=(0, SPACING["md"]))
        input_frame.columnconfigure(0, weight=1)

        self.query_var = ctk.StringVar()
        self.query_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.query_var,
            placeholder_text="Ask Agency Copilot or type 'Ctrl+K' for suggestions...",
            font=FONTS["body"],
            height=42,
            corner_radius=RADIUS["sm"]
        )
        self.query_entry.grid(row=0, column=0, sticky="ew", padx=(0, SPACING["md"]))
        self.query_entry.bind("<Return>", lambda e: self.send_message())

        ctk.CTkButton(
            input_frame,
            text="Send ↵",
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            height=42,
            width=90,
            corner_radius=RADIUS["sm"],
            command=self.send_message
        ).grid(row=0, column=1)

    # ── RIGHT PANE BUILDER ──────────────────────────────────────
    def _build_right_pane(self):
        container = ctk.CTkScrollableFrame(self.right_pane, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        ctk.CTkLabel(container, text="BUSINESS CONTEXT", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, SPACING["xs"]))

        # Business Card Header
        self.ctx_name_lbl = ctk.CTkLabel(container, text="No Business Selected", font=FONTS["heading2"], text_color=COLORS["text"])
        self.ctx_name_lbl.pack(anchor="w")

        self.ctx_cat_lbl = ctk.CTkLabel(container, text="Select a prospect to inspect", font=FONTS["caption"], text_color=COLORS["text_muted"])
        self.ctx_cat_lbl.pack(anchor="w", pady=(0, SPACING["md"]))

        # Key Metrics Grid
        self.ctx_score_lbl = self._create_info_card(container, "Opportunity Score", "N/A", COLORS["primary"])
        self.ctx_rating_lbl = self._create_info_card(container, "Google Rating", "N/A", COLORS["warning"])
        self.ctx_web_lbl = self._create_info_card(container, "Website Status", "N/A", COLORS["text_secondary"])
        self.ctx_rev_lbl = self._create_info_card(container, "Est. Revenue", "₹0", COLORS["success"])

        # Audit Badges Section
        ctk.CTkLabel(container, text="AI OPPORTUNITY AUDIT", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(SPACING["md"], SPACING["xs"]))
        self.badges_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.badges_frame.pack(fill="x")

        # Quick Actions Box
        ctk.CTkLabel(container, text="INSTANT ACTIONS", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", pady=(SPACING["md"], SPACING["xs"]))
        ctk.CTkButton(
            container, text="Generate Sales Package", font=FONTS["body_sm"], fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"], corner_radius=RADIUS["sm"], height=32, command=self._action_gen_package
        ).pack(fill="x", pady=SPACING["xs"])

        ctk.CTkButton(
            container, text="Move to Proposal Stage", font=FONTS["body_sm"], fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_elevated"], corner_radius=RADIUS["sm"], height=32, command=self._action_move_proposal
        ).pack(fill="x", pady=SPACING["xs"])

    def _create_info_card(self, parent, title: str, val: str, val_color: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=SPACING["3xs"])
        ctk.CTkLabel(card, text=title, font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
        lbl = ctk.CTkLabel(card, text=val, font=FONTS["heading3"], text_color=val_color)
        lbl.pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))
        return lbl

    # ── LOGIC & MESSAGE HANDLING ────────────────────────────────
    def load_leads(self):
        self.leads = get_all_leads()
        names = [l.business_name for l in self.leads]
        if names:
            self.context_dropdown.configure(values=names)

    def _on_context_selected(self, selected_name: str):
        for l in self.leads:
            if l.business_name == selected_name:
                self.selected_lead = l
                self._update_context_inspector(l)
                break

    def _update_context_inspector(self, lead):
        self.ctx_name_lbl.configure(text=lead.business_name)
        self.ctx_cat_lbl.configure(text=f"{lead.category or 'General'} • {lead.city or 'Local'}")

        score = lead.opportunity_score or 0
        score_color = "#FF4B4B" if score >= 60 else "#FFD166" if score >= 30 else "#118AB2"
        self.ctx_score_lbl.configure(text=f"{score} / 100", text_color=score_color)

        rating = f"★ {lead.rating}" if lead.rating else "N/A"
        self.ctx_rating_lbl.configure(text=rating)

        self.ctx_web_lbl.configure(text=lead.website_type or "Unknown")

        val = f"₹{lead.estimated_value:,.0f}" if lead.estimated_value else "₹0"
        self.ctx_rev_lbl.configure(text=val)

        # Clear & render badges
        for w in self.badges_frame.winfo_children():
            w.destroy()

        badges = []
        if lead.website_type == "None":
            badges.append("🚨 No Website")
        elif lead.website_type in ["Facebook", "Instagram", "WhatsApp"]:
            badges.append("⚠️ Social Only")

        if lead.has_ssl == "No":
            badges.append("🔒 No SSL")
        if lead.is_mobile_responsive == "No":
            badges.append("📱 Not Responsive")

        if not badges:
            badges.append("✓ Standard Setup")

        for b in badges:
            badge_card = ctk.CTkLabel(
                self.badges_frame, text=b, font=FONTS["caption"], text_color=COLORS["text"],
                fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"], padx=SPACING["xs"], pady=2
            )
            badge_card.pack(anchor="w", pady=2)

    def _append_system_welcome(self):
        self.append_chat_message(
            "Copilot",
            "Hello! I am **Agency Copilot**, your autonomous intelligence engine. I can analyze CRM opportunities, estimate deal values, draft outreach packages, or execute strategic queries.\n\nTry clicking a **Quick Action** above or type your goal below."
        )

    def append_chat_message(self, sender: str, text: str):
        is_user = sender == "You"
        align = "e" if is_user else "w"
        bg_color = COLORS["primary_muted"] if is_user else COLORS["surface_light"]

        msg_card = ctk.CTkFrame(
            self.chat_scroll,
            fg_color=bg_color,
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"]
        )
        msg_card.pack(anchor=align, fill="x", pady=SPACING["xs"], padx=SPACING["sm"])

        header = ctk.CTkLabel(
            msg_card, text=sender, font=FONTS["caption"],
            text_color=COLORS["primary"] if not is_user else COLORS["background"]
        )
        header.pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))

        content = ctk.CTkLabel(
            msg_card, text=text, font=FONTS["body"],
            text_color=COLORS["text"] if not is_user else COLORS["background"],
            justify="left", wraplength=550
        )
        content.pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))

        # Scroll to bottom
        self.chat_scroll.after(10, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    def send_message(self):
        query = self.query_var.get().strip()
        if not query:
            return
        self.query_var.set("")
        self.append_chat_message("You", query)

        # Process through FORGE OS Planner
        threading.Thread(target=self._process_ai_query, args=(query,), daemon=True).start()

    def _process_ai_query(self, query: str):
        res = planner.execute_query(query)
        if res["success"]:
            reply = f"**{res['intent'].upper()} EXECUTION**:\n{res['recommendation']}\n\nData Payload:\n{res['data']}"
        else:
            if self.selected_lead:
                reply = f"Executing customized strategy for **{self.selected_lead.business_name}**...\n\nOpportunity Score: {self.selected_lead.opportunity_score}/100\nRecommended Outreach: WhatsApp Pitch & PDF Proposal."
            else:
                reply = "I parsed your request. Select a business from the left context dropdown or choose a Quick Action pill to auto-generate content."

        self.after(0, lambda: self.append_chat_message("Copilot", reply))

    def _execute_quick_action(self, prompt: str):
        if not self.selected_lead:
            toast_manager.show("Select a business context first!", "warning")
            return
        self.append_chat_message("You", f"Execute: {prompt}")

        def _worker():
            lead = self.selected_lead
            if prompt == "Generate cold outreach email":
                draft = email_gen.generate(lead)
                update_lead(lead.id, {"email_draft": draft})
                reply = f"**Generated Cold Email for {lead.business_name}**:\n\n{draft}"
            elif prompt == "Generate WhatsApp pitch message":
                draft = whatsapp_gen.generate(lead)
                update_lead(lead.id, {"whatsapp_draft": draft})
                reply = f"**Generated WhatsApp Pitch for {lead.business_name}**:\n\n{draft}"
            elif prompt == "Generate custom website proposal":
                prop = proposal_gen.generate(lead)
                update_lead(lead.id, {"proposal": prop})
                reply = f"**Generated Proposal for {lead.business_name}**:\n\n{prop}"
            else:
                reply = f"**Strategic Plan for {lead.business_name}** ({prompt}):\n- Opportunity Score: {lead.opportunity_score}/100\n- Est. Project Value: ₹{lead.estimated_value:,.0f}\n- Priority: {lead.priority}"

            self.after(0, lambda: self.append_chat_message("Copilot", reply))

        threading.Thread(target=_worker, daemon=True).start()

    def _insert_template(self, template_name: str):
        self.query_var.set(f"Apply template: {template_name}")

    def _new_session(self):
        for w in self.chat_scroll.winfo_children():
            w.destroy()
        self._append_system_welcome()

    def _action_gen_package(self):
        if not self.selected_lead:
            toast_manager.show("Select a business context first!", "warning")
            return

        def _worker():
            lead = self.selected_lead
            lead.proposal = proposal_gen.generate(lead)
            lead.email_draft = email_gen.generate(lead)
            lead.whatsapp_draft = whatsapp_gen.generate(lead)
            lead.call_script = call_script_gen.generate(lead)
            lead.meeting_points = meeting_points_gen.generate(lead)
            update_lead(lead.id, {
                "proposal": lead.proposal,
                "email_draft": lead.email_draft,
                "whatsapp_draft": lead.whatsapp_draft,
                "call_script": lead.call_script,
                "meeting_points": lead.meeting_points
            })
            self.after(0, lambda: toast_manager.show("Sales package generated!", "success"))
            self.after(0, lambda: self.append_chat_message("Copilot", f"Generated full sales package for **{lead.business_name}**! Proposals, scripts, emails, and WhatsApp drafts are ready in the database."))

        threading.Thread(target=_worker, daemon=True).start()

    def _action_move_proposal(self):
        if not self.selected_lead:
            return
        update_lead(self.selected_lead.id, {"status": "Proposal"})
        toast_manager.show(f"Moved {self.selected_lead.business_name} to Proposal stage", "success")
