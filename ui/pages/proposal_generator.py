"""
AI Sales Studio Page for LeadForge AI.
Features a 3-pane enterprise workspace: Searchable Business Card Index, Collapsible Section Proposal Editor,
Action Toolbar (PDF Export, Tone Switcher, Outreach Triggers), and Live Proposal Telemetry.
"""

import customtkinter as ctk
import webbrowser
import urllib.parse
import threading
from typing import Dict, List, Optional, Any

from core.config import COLORS, FONTS, SPACING, RADIUS
from core.logger import logger
from database.crud import get_all_leads, update_lead
from services.ai_generators import proposal_gen
from ui.components.toast import toast_manager


class CollapsibleSectionCard(ctk.CTkFrame):
    """
    A collapsible card component for individual proposal sections.
    """
    def __init__(self, master, title: str, content: str = "", on_change_callback=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        self.title_str = title
        self.on_change_callback = on_change_callback
        self.is_expanded = True

        # Header Bar
        self.header_bar = ctk.CTkFrame(self, fg_color="transparent", height=38)
        self.header_bar.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        self.toggle_btn = ctk.CTkButton(
            self.header_bar,
            text="▼",
            width=24,
            height=24,
            fg_color="transparent",
            text_color=COLORS["primary"],
            hover_color=COLORS["surface_light"],
            command=self.toggle
        )
        self.toggle_btn.pack(side="left", padx=(0, SPACING["xs"]))

        self.title_label = ctk.CTkLabel(
            self.header_bar,
            text=title,
            font=FONTS["heading3"],
            text_color=COLORS["text"]
        )
        self.title_label.pack(side="left")

        # Content Frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        self.textbox = ctk.CTkTextbox(
            self.content_frame,
            font=FONTS["body"],
            fg_color=COLORS["surface_light"],
            text_color=COLORS["text"],
            corner_radius=RADIUS["sm"],
            border_width=1,
            border_color=COLORS["border"],
            height=90,
            wrap="word"
        )
        self.textbox.pack(fill="x", expand=True)
        if content:
            self.textbox.insert("1.0", content)

        self.textbox.bind("<KeyRelease>", self._on_text_changed)

    def toggle(self):
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.toggle_btn.configure(text="▶")
            self.is_expanded = False
        else:
            self.content_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))
            self.toggle_btn.configure(text="▼")
            self.is_expanded = True

    def get_text(self) -> str:
        return self.textbox.get("1.0", "end-1c").strip()

    def set_text(self, text: str):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)

    def _on_text_changed(self, event=None):
        if self.on_change_callback:
            self.on_change_callback()


class ProposalGeneratorPage(ctk.CTkFrame):
    """
    AI Sales Studio 3-Pane Page Implementation.
    """
    SECTION_HEADERS = [
        "Executive Summary",
        "Business & Market Analysis",
        "Website Audit & Findings",
        "Core Problems & Bottlenecks",
        "Business Revenue Impact",
        "Recommended Solution & Tech Stack",
        "Portfolio References",
        "Estimated Pricing & Investment",
        "Project Timeline & Milestones",
        "Deliverables & Guarantees",
        "Call To Action"
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.leads_data: List[Any] = []
        self.selected_lead: Optional[Any] = None
        self.favorites: Set[int] = set()
        self.section_cards: Dict[str, CollapsibleSectionCard] = {}

        # ── Page Header ──────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, SPACING["md"]))

        ctk.CTkLabel(
            header_frame,
            text="AI Sales Studio",
            font=FONTS["heading1"],
            text_color=COLORS["text"]
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="Enterprise Proposal & Pitch Workspace",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=SPACING["md"], pady=(4, 0))

        # ── 3-Pane Grid Container ────────────────────────────────
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        body_frame.columnconfigure(1, weight=1)
        body_frame.rowconfigure(0, weight=1)

        # ── LEFT PANE: Searchable Business Index ────────────────
        self.left_pane = ctk.CTkFrame(
            body_frame,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            width=280
        )
        self.left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["md"]))
        self.left_pane.pack_propagate(False)

        self._build_left_pane()

        # ── CENTER PANE: Structured Section Editor Workspace ───
        self.center_pane = ctk.CTkFrame(
            body_frame,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.center_pane.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING["md"]))

        self._build_center_pane()

        # ── RIGHT PANE: Live Telemetry & Analytics ──────────────
        self.right_pane = ctk.CTkFrame(
            body_frame,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            width=260
        )
        self.right_pane.grid(row=0, column=2, sticky="nsew")
        self.right_pane.pack_propagate(False)

        self._build_right_pane()

        self.load_leads()

    # ── LEFT PANE BUILDER ───────────────────────────────────────
    def _build_left_pane(self):
        # Header & Search
        search_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        search_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])

        ctk.CTkLabel(
            search_frame,
            text="PROSPECT INDEX",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, SPACING["xs"]))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search business...",
            font=FONTS["body"],
            height=32,
            corner_radius=RADIUS["sm"]
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_leads())

        # Filters row
        filter_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        filter_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        self.priority_filter_var = ctk.StringVar(value="All Priorities")
        self.priority_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Priorities", "High Opportunity", "Medium", "Low"],
            variable=self.priority_filter_var,
            font=FONTS["caption"],
            height=26,
            corner_radius=RADIUS["sm"],
            command=lambda v: self._filter_leads()
        )
        self.priority_dropdown.pack(side="left", fill="x", expand=True)

        # Scrollable Cards Container
        self.cards_scroll = ctk.CTkScrollableFrame(self.left_pane, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True, padx=SPACING["xs"], pady=(0, SPACING["sm"]))

    # ── CENTER PANE BUILDER ──────────────────────────────────────
    def _build_center_pane(self):
        self.center_pane.rowconfigure(1, weight=1)
        self.center_pane.columnconfigure(0, weight=1)

        # Top Toolbar
        self.toolbar = ctk.CTkFrame(self.center_pane, fg_color=COLORS["surface_light"], height=48, corner_radius=RADIUS["md"])
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["md"])

        # Generate Button
        self.gen_btn = ctk.CTkButton(
            self.toolbar,
            text="⚡ Generate AI Proposal",
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            corner_radius=RADIUS["sm"],
            height=32,
            command=self._generate_proposal_ai
        )
        self.gen_btn.pack(side="left", padx=SPACING["sm"], pady=SPACING["xs"])

        # Tone Selector
        self.tone_var = ctk.StringVar(value="Tone: Professional")
        self.tone_menu = ctk.CTkOptionMenu(
            self.toolbar,
            values=["Tone: Professional", "Tone: Aggressive", "Tone: Friendly", "Tone: Direct"],
            variable=self.tone_var,
            font=FONTS["caption"],
            width=120,
            height=32,
            corner_radius=RADIUS["sm"]
        )
        self.tone_menu.pack(side="left", padx=SPACING["xs"])

        # Actions on right
        ctk.CTkButton(
            self.toolbar, text="WhatsApp", font=FONTS["caption"], fg_color="#25D366", hover_color="#128C7E",
            height=32, width=70, corner_radius=RADIUS["sm"], command=self._send_whatsapp
        ).pack(side="right", padx=(0, SPACING["sm"]))

        ctk.CTkButton(
            self.toolbar, text="Email", font=FONTS["caption"], fg_color=COLORS["surface_elevated"],
            height=32, width=60, corner_radius=RADIUS["sm"], command=self._send_email
        ).pack(side="right", padx=SPACING["xs"])

        ctk.CTkButton(
            self.toolbar, text="Copy", font=FONTS["caption"], fg_color=COLORS["surface_elevated"],
            height=32, width=60, corner_radius=RADIUS["sm"], command=self._copy_proposal
        ).pack(side="right", padx=SPACING["xs"])

        # Scrollable Sections Container
        self.editor_scroll = ctk.CTkScrollableFrame(self.center_pane, fg_color="transparent")
        self.editor_scroll.grid(row=1, column=0, sticky="nsew", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Build Collapsible Section Cards
        self.section_cards.clear()
        for title in self.SECTION_HEADERS:
            card = CollapsibleSectionCard(
                self.editor_scroll,
                title=title,
                on_change_callback=self._auto_save_proposal
            )
            card.pack(fill="x", pady=SPACING["xs"])
            self.section_cards[title] = card

    # ── RIGHT PANE BUILDER ──────────────────────────────────────
    def _build_right_pane(self):
        container = ctk.CTkScrollableFrame(self.right_pane, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        ctk.CTkLabel(
            container, text="PROPOSAL TELEMETRY", font=FONTS["caption"], text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, SPACING["sm"]))

        # Opportunity Score Frame
        self.telemetry_score_lbl = self._create_telemetry_card(container, "Opportunity Score", "0 / 100", COLORS["primary"])
        self.telemetry_revenue_lbl = self._create_telemetry_card(container, "Estimated Revenue", "₹0", COLORS["success"])
        self.telemetry_close_lbl = self._create_telemetry_card(container, "Close Probability", "0%", COLORS["warning"])
        self.telemetry_quality_lbl = self._create_telemetry_card(container, "Proposal Quality", "0 / 100", COLORS["accent"])
        self.telemetry_read_lbl = self._create_telemetry_card(container, "Reading Time", "0 min", COLORS["text_secondary"])
        self.telemetry_confidence_lbl = self._create_telemetry_card(container, "AI Confidence Level", "High", COLORS["success"])

        # Next Action Box
        next_box = ctk.CTkFrame(container, fg_color=COLORS["surface_light"], corner_radius=RADIUS["md"], border_width=1, border_color=COLORS["border"])
        next_box.pack(fill="x", pady=SPACING["md"])

        ctk.CTkLabel(next_box, text="SUGGESTED NEXT ACTION", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
        self.next_action_lbl = ctk.CTkLabel(next_box, text="Select a prospect to generate proposal", font=FONTS["body_sm"], text_color=COLORS["text"], wraplength=200, justify="left")
        self.next_action_lbl.pack(anchor="w", padx=SPACING["sm"], pady=SPACING["xs"])

    def _create_telemetry_card(self, parent, title: str, value: str, value_color: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_light"], corner_radius=RADIUS["sm"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=SPACING["xs"])
        ctk.CTkLabel(card, text=title, font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
        lbl = ctk.CTkLabel(card, text=value, font=FONTS["heading3"], text_color=value_color)
        lbl.pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))
        return lbl

    # ── DATA LOADING & FILTERING ────────────────────────────────
    def load_leads(self):
        self.leads_data = get_all_leads()
        self._filter_leads()

    def _filter_leads(self):
        query = self.search_var.get().lower().strip()
        p_filter = self.priority_filter_var.get()

        for w in self.cards_scroll.winfo_children():
            w.destroy()

        filtered = []
        for l in self.leads_data:
            if query and query not in l.business_name.lower():
                continue
            if p_filter != "All Priorities" and l.priority != p_filter:
                continue
            filtered.append(l)

        if not filtered:
            ctk.CTkLabel(self.cards_scroll, text="No prospects found.", font=FONTS["body_sm"], text_color=COLORS["text_muted"]).pack(pady=SPACING["lg"])
            return

        for lead in filtered:
            card = self._create_business_card(lead)
            card.pack(fill="x", pady=SPACING["xs"])

        # Select first lead if none selected
        if filtered and not self.selected_lead:
            self._select_lead(filtered[0])

    def _create_business_card(self, lead) -> ctk.CTkFrame:
        is_selected = self.selected_lead and self.selected_lead.id == lead.id
        bg = COLORS["surface_elevated"] if is_selected else COLORS["surface_light"]

        card = ctk.CTkFrame(self.cards_scroll, fg_color=bg, corner_radius=RADIUS["sm"], border_width=1, border_color=COLORS["border"])

        # Click selection
        card.bind("<Button-1>", lambda e, l=lead: self._select_lead(l))

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
        top.bind("<Button-1>", lambda e, l=lead: self._select_lead(l))

        name_lbl = ctk.CTkLabel(top, text=lead.business_name, font=FONTS["heading3"], text_color=COLORS["text"])
        name_lbl.pack(side="left")
        name_lbl.bind("<Button-1>", lambda e, l=lead: self._select_lead(l))

        score = lead.opportunity_score or 0
        score_color = "#FF4B4B" if score >= 60 else "#FFD166" if score >= 30 else "#118AB2"
        score_lbl = ctk.CTkLabel(top, text=f"{score}", font=FONTS["caption"], text_color=score_color)
        score_lbl.pack(side="right")

        bot = ctk.CTkFrame(card, fg_color="transparent")
        bot.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["xs"]))
        bot.bind("<Button-1>", lambda e, l=lead: self._select_lead(l))

        val = f"₹{lead.estimated_value:,.0f}" if lead.estimated_value else "₹0"
        val_lbl = ctk.CTkLabel(bot, text=f"{lead.category or 'General'} • {val}", font=FONTS["caption"], text_color=COLORS["text_muted"])
        val_lbl.pack(side="left")
        val_lbl.bind("<Button-1>", lambda e, l=lead: self._select_lead(l))

        return card

    def _select_lead(self, lead):
        self.selected_lead = lead
        self._filter_leads() # Refresh highlight

        # Parse proposal into sections
        text = lead.proposal or ""
        self._populate_proposal_sections(text)
        self._update_telemetry(lead)

    def _populate_proposal_sections(self, full_text: str):
        if not full_text:
            for card in self.section_cards.values():
                card.set_text("")
            return

        # Simple section parser based on headers
        lines = full_text.split("\n")
        current_header = None
        buffer = {}

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("# "):
                header_name = stripped.replace("## ", "").replace("# ", "").strip()
                # Find matching section header
                matched = None
                for sec in self.SECTION_HEADERS:
                    if sec.lower() in header_name.lower():
                        matched = sec
                        break
                current_header = matched or "Executive Summary"
                if current_header not in buffer:
                    buffer[current_header] = []
            elif current_header:
                buffer[current_header].append(line)

        for sec_title, card in self.section_cards.items():
            if sec_title in buffer:
                card.set_text("\n".join(buffer[sec_title]).strip())
            else:
                card.set_text("")

    def _update_telemetry(self, lead):
        score = lead.opportunity_score or 0
        self.telemetry_score_lbl.configure(text=f"{score} / 100")

        val = f"₹{lead.estimated_value:,.0f}" if lead.estimated_value else "₹0"
        self.telemetry_revenue_lbl.configure(text=val)

        close_prob = min(95, max(20, int(score * 0.9)))
        self.telemetry_close_lbl.configure(text=f"{close_prob}%")

        q_score = min(98, max(40, 50 + len(lead.proposal or "") // 50))
        self.telemetry_quality_lbl.configure(text=f"{q_score} / 100")

        words = len((lead.proposal or "").split())
        read_time = max(1, round(words / 200, 1))
        self.telemetry_read_lbl.configure(text=f"{read_time} min")

        self.next_action_lbl.configure(
            text="Send tailored proposal via WhatsApp or Email client to lock in discovery meeting."
        )

    def _generate_proposal_ai(self):
        if not self.selected_lead:
            toast_manager.show("Select a prospect first", "warning")
            return

        def _worker():
            prop_text = proposal_gen.generate(self.selected_lead)
            update_lead(self.selected_lead.id, {"proposal": prop_text})
            self.selected_lead.proposal = prop_text
            self.after(0, lambda: self._select_lead(self.selected_lead))
            self.after(0, lambda: toast_manager.show("Proposal generated successfully!", "success"))

        threading.Thread(target=_worker, daemon=True).start()

    def _auto_save_proposal(self):
        if not self.selected_lead:
            return

        # Reconstruct full proposal text
        full_markdown = []
        for title, card in self.section_cards.items():
            content = card.get_text()
            if content:
                full_markdown.append(f"## {title}\n{content}\n")

        new_text = "\n".join(full_markdown)
        self.selected_lead.proposal = new_text
        update_lead(self.selected_lead.id, {"proposal": new_text})

    def _copy_proposal(self):
        if not self.selected_lead or not self.selected_lead.proposal:
            toast_manager.show("No proposal to copy", "warning")
            return
        self.clipboard_clear()
        self.clipboard_append(self.selected_lead.proposal)
        toast_manager.show("Proposal copied to clipboard!", "success")

    def _send_email(self):
        if not self.selected_lead:
            return
        email = self.selected_lead.email or "contact@example.com"
        subject = urllib.parse.quote(f"Website Opportunity for {self.selected_lead.business_name}")
        body = urllib.parse.quote(self.selected_lead.proposal or "")
        webbrowser.open(f"mailto:{email}?subject={subject}&body={body}")

    def _send_whatsapp(self):
        if not self.selected_lead:
            return
        phone = "".join(filter(str.isdigit, self.selected_lead.phone or ""))
        text = urllib.parse.quote(f"Hi {self.selected_lead.business_name},\nHere is your custom proposal:\n\n{self.selected_lead.proposal or ''}")
        webbrowser.open(f"https://wa.me/{phone}?text={text}")
