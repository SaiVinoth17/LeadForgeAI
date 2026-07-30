import customtkinter as ctk
import threading
import os
import webbrowser
import urllib.parse
from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import get_all_leads, update_lead, delete_lead, db_manager
from exports.exporter import Exporter
from core.task_manager import task_manager
from services.screenshot_engine import screenshot_engine
from services.analyzer import WebsiteAnalyzer
from services.ai_generators import proposal_gen, email_gen, whatsapp_gen, call_script_gen, meeting_points_gen
from core.logger import logger
from ui.components.playwright_installer import check_playwright_installed, PlaywrightInstallerModal
from ui.components.toast import toast_manager

# Kanban column config: (status_key, display_name, accent_color, bg_tint)
KANBAN_COLUMNS = [
    ("Discovery",   "Discovery",    COLORS["primary"],  COLORS["kanban_discovery"]),
    ("Qualified",   "Qualified",    COLORS["accent"],   COLORS["kanban_qualified"]),
    ("Proposal",    "Proposal",     COLORS["info"],     COLORS["kanban_proposal"]),
    ("Meeting",     "Meeting",      COLORS["success"],  COLORS["kanban_meeting"]),
    ("Negotiation", "Negotiation",  COLORS["warning"],  COLORS["kanban_negotiation"]),
    ("Won",         "Won",          COLORS["success"],  COLORS["kanban_won"]),
    ("Lost",        "Lost",         COLORS["danger"],   COLORS["kanban_lost"]),
]

class CRMPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        # ── Header ────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))
        header_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, text="Pipeline",
            font=FONTS["heading1"], text_color=COLORS["text"]
        ).grid(row=0, column=0, sticky="w")
        
        # ── Filter Bar ────────────────────────────────────
        self.filter_frame = ctk.CTkFrame(
            self, fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["md"]))
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.filter_frame, textvariable=self.search_var,
            placeholder_text="Search opportunities...",
            width=220, corner_radius=RADIUS["sm"],
            fg_color=COLORS["surface_light"],
            border_color=COLORS["border"],
            border_width=1
        )
        self.search_entry.pack(side="left", padx=SPACING["md"], pady=SPACING["sm"])
        self._search_debounce_job = None
        self.search_entry.bind("<KeyRelease>", self._on_search_key_release)
        
        self.sort_var = ctk.StringVar(value="Opportunity (High to Low)")
        self.sort_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Opportunity (High to Low)", "Recent", "Status"],
            variable=self.sort_var,
            command=lambda e: self.load_leads(),
            corner_radius=RADIUS["sm"],
            fg_color=COLORS["surface_light"],
            button_color=COLORS["surface_elevated"],
            button_hover_color=COLORS["border_light"]
        )
        self.sort_menu.pack(side="left", padx=SPACING["sm"])

        # Action buttons (right side)
        btn_style = {
            "height": 32, "corner_radius": RADIUS["sm"],
            "font": FONTS["small"]
        }
        ctk.CTkButton(
            self.filter_frame, text="Export CSV",
            command=self.export_csv,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_elevated"],
            text_color=COLORS["text_secondary"],
            **btn_style
        ).pack(side="right", padx=SPACING["xs"])
        ctk.CTkButton(
            self.filter_frame, text="Export Excel",
            command=self.export_excel,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_elevated"],
            text_color=COLORS["text_secondary"],
            **btn_style
        ).pack(side="right", padx=SPACING["xs"])
        ctk.CTkButton(
            self.filter_frame, text="Export PDF",
            command=self.export_pdf,
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_elevated"],
            text_color=COLORS["text_secondary"],
            **btn_style
        ).pack(side="right", padx=SPACING["xs"])
        
        # ── Kanban Board ──────────────────────────────────
        self.kanban_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", orientation="horizontal"
        )
        self.kanban_container.grid(row=2, column=0, sticky="nsew")
        
        self.leads_data = []
        self.columns_frames = {}
        self.column_count_labels = {}
        
        self.statuses = [c[0] for c in KANBAN_COLUMNS]
        
        for status_key, display_name, accent, bg_tint in KANBAN_COLUMNS:
            col_frame = ctk.CTkFrame(
                self.kanban_container,
                fg_color=bg_tint,
                corner_radius=RADIUS["lg"],
                width=300,
                border_width=1,
                border_color=COLORS["border"]
            )
            col_frame.pack(side="left", fill="y", padx=SPACING["xs"], pady=SPACING["xs"])
            col_frame.pack_propagate(False)
            
            # Column header
            header_bar = ctk.CTkFrame(col_frame, fg_color="transparent")
            header_bar.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))
            
            # Accent dot + name
            ctk.CTkLabel(
                header_bar, text="●",
                font=("Segoe UI", 8), text_color=accent
            ).pack(side="left", padx=(0, SPACING["sm"]))
            
            ctk.CTkLabel(
                header_bar, text=display_name.upper(),
                font=FONTS["caption"], text_color=COLORS["text_muted"]
            ).pack(side="left")
            
            # Count badge
            count_lbl = ctk.CTkLabel(
                header_bar, text="0",
                font=FONTS["badge"],
                text_color=COLORS["text_tertiary"],
                fg_color=COLORS["surface_elevated"],
                corner_radius=RADIUS["sm"],
                padx=8, pady=2
            )
            count_lbl.pack(side="right")
            self.column_count_labels[status_key] = count_lbl
            
            # Scrollable card area
            scroll_area = ctk.CTkScrollableFrame(col_frame, fg_color="transparent")
            scroll_area.pack(fill="both", expand=True, padx=SPACING["xs"], pady=(0, SPACING["xs"]))
            
            self.columns_frames[status_key] = scroll_area
            
        self.load_leads()

    def _on_search_key_release(self, event=None):
        if self._search_debounce_job:
            self.after_cancel(self._search_debounce_job)
        self._search_debounce_job = self.after(250, self.load_leads)

    def load_leads(self):
        for status, frame in self.columns_frames.items():
            for widget in frame.winfo_children():
                widget.destroy()
            
        leads = get_all_leads()
        search_q = self.search_var.get().lower()
        if search_q:
            leads = [l for l in leads if search_q in l.business_name.lower() or (l.category and search_q in l.category.lower())]
            
        sort_opt = self.sort_var.get()
        if sort_opt == "Opportunity (High to Low)":
            leads.sort(key=lambda x: x.opportunity_score or 0, reverse=True)
        elif sort_opt == "Recent":
            leads.sort(key=lambda x: x.created_date.timestamp() if x.created_date else 0, reverse=True)
            
        self.leads_data = leads
        
        # Count per column
        counts = {s: 0 for s in self.statuses}
        for lead in leads[:200]:
            status = lead.status if lead.status in self.statuses else "Discovery"
            counts[status] = counts.get(status, 0) + 1
            
        # Update count badges
        for status, lbl in self.column_count_labels.items():
            lbl.configure(text=str(counts.get(status, 0)))

        # Incremental rendering to prevent UI freeze
        self._render_batch_id = getattr(self, "_render_batch_id", 0) + 1
        self._render_leads_batch(leads[:200], 0, self._render_batch_id)

    def _render_leads_batch(self, leads_to_render, index, batch_id):
        # Abort if a new load_leads was called
        if batch_id != getattr(self, "_render_batch_id", 0):
            return
            
        # Render a small batch of cards
        batch_size = 10
        end_index = min(index + batch_size, len(leads_to_render))
        
        for i in range(index, end_index):
            lead = leads_to_render[i]
            status = lead.status if lead.status in self.statuses else "Discovery"
            parent = self.columns_frames[status]
            self._create_kanban_card(parent, lead)
            
        if end_index < len(leads_to_render):
            self.after(20, self._render_leads_batch, leads_to_render, end_index, batch_id)

    def _create_kanban_card(self, parent, lead):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=SPACING["xs"], padx=SPACING["xs"])
        
        # ── Name + Score ──────────────────────────────────
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))
        
        ctk.CTkLabel(
            top, text=lead.business_name,
            font=FONTS["heading3"],
            text_color=COLORS["text"],
            wraplength=190, justify="left"
        ).pack(side="left", anchor="w")
        
        score = lead.opportunity_score or 0
        score_color = COLORS["success"] if score >= 60 else COLORS["warning"] if score >= 30 else COLORS["text_muted"]
        ctk.CTkLabel(
            top, text=str(score),
            font=FONTS["heading3"],
            text_color=score_color
        ).pack(side="right")
        
        # ── Category + Type ───────────────────────────────
        ctk.CTkLabel(
            card,
            text=f"{lead.category or '—'}  ·  {lead.website_type or 'Unknown'}",
            font=FONTS["small"],
            text_color=COLORS["text_tertiary"]
        ).pack(anchor="w", padx=SPACING["md"])
        
        # ── Quick Actions ─────────────────────────────────
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["md"]))
        
        btn_s = {"height": 28, "corner_radius": RADIUS["sm"], "font": FONTS["badge"]}
        
        idx = self.statuses.index(lead.status) if lead.status in self.statuses else 0
        if idx > 0:
            ctk.CTkButton(
                action_frame, text="←", width=28,
                fg_color=COLORS["surface_light"],
                hover_color=COLORS["surface_elevated"],
                text_color=COLORS["text_muted"],
                command=lambda l=lead.id, s=self.statuses[idx-1]: self.update_status(l, s),
                **btn_s
            ).pack(side="left", padx=2)
            
        ctk.CTkButton(
            action_frame, text="View", width=50,
            fg_color=COLORS["primary_muted"],
            hover_color=COLORS["primary"],
            text_color=COLORS["primary"],
            command=lambda l=lead.id: self.view_details(l),
            **btn_s
        ).pack(side="left", padx=2, expand=True)
        
        ctk.CTkButton(
            action_frame, text="Pkg", width=40,
            fg_color=COLORS["accent_muted"],
            hover_color=COLORS["accent"],
            text_color=COLORS["accent"],
            command=lambda l=lead.id: self.generate_sales_package(l),
            **btn_s
        ).pack(side="left", padx=2, expand=True)
        
        ctk.CTkButton(
            action_frame, text="Export", width=48,
            fg_color=COLORS["success_muted"],
            hover_color=COLORS["success"],
            text_color=COLORS["success"],
            command=lambda l=lead.id: self.export_lead_package(l),
            **btn_s
        ).pack(side="left", padx=2, expand=True)
        
        if idx < len(self.statuses) - 1:
            ctk.CTkButton(
                action_frame, text="→", width=28,
                fg_color=COLORS["surface_light"],
                hover_color=COLORS["surface_elevated"],
                text_color=COLORS["text_muted"],
                command=lambda l=lead.id, s=self.statuses[idx+1]: self.update_status(l, s),
                **btn_s
            ).pack(side="right", padx=2)

    def export_lead_package(self, lead_id):
        lead = next((l for l in self.leads_data if l.id == lead_id), None)
        if not lead: return
        folder = Exporter().export_client_package(lead)
        if folder:
            toast_manager.show(f"Exported to {folder.name}", "success")
            os.startfile(folder)
        else:
            toast_manager.show("Export failed", "error")

    def _get_selected_ids(self):
        return []
        
    def update_status(self, lead_id, new_status):
        update_lead(lead_id, {"status": new_status})
        self.load_leads()
        toast_manager.show(f"Moved to {new_status}", "success")

    def bulk_delete(self):
        toast_manager.show("Bulk delete is disabled in Pipeline view.", "warning")
        
    def view_details(self, lead_id):
        lead = next((l for l in self.leads_data if l.id == lead_id), None)
        if not lead: return
        LeadDetailsModal(self, lead)
        
    def bulk_generate(self):
        for lid in self._get_selected_ids():
            self.generate_sales_package(lid)
            
    def generate_sales_package(self, lead_id):
        if not check_playwright_installed():
            PlaywrightInstallerModal(self.winfo_toplevel(), on_success_callback=lambda: self._start_sales_package(lead_id))
        else:
            self._start_sales_package(lead_id)
            
    def _start_sales_package(self, lead_id):
        toast_manager.show("Generating sales package...", "info")
        task_manager.add_task(self._task_sales_package, lead_id)
        
    def _task_sales_package(self, lead_id):
        from models.lead import Lead
        session = db_manager.get_session()
        try:
            db_lead = session.query(Lead).filter(Lead.id == lead_id).first()
            if not db_lead: return
            
            logger.info(f"Generating Sales Package for {db_lead.business_name}...")
            
            if db_lead.website_type == "Professional":
                analyzer = WebsiteAnalyzer(db_lead)
                results = analyzer.run_analysis()
                screenshot_engine.capture(db_lead.id)
                
                db_lead.opportunity_score = results.get("opportunity_score", 0)
                db_lead.priority = results.get("lead_priority", "Cold")
                db_lead.ai_summary = results.get("ai_summary", "")
                db_lead.estimated_value = results.get("estimated_value", 0.0)
                db_lead.confidence_score = results.get("confidence_score", 0)
                db_lead.confidence_reasons = results.get("confidence_reasons", "")
                
            # Generate Texts (Skip if already exists)
            if not db_lead.proposal:
                db_lead.proposal = proposal_gen.generate(db_lead)
                logger.info(f"Generated new Proposal for {db_lead.business_name}")
            else:
                logger.info(f"Using cached Proposal for {db_lead.business_name}")
                
            if not db_lead.email_draft:
                db_lead.email_draft = email_gen.generate(db_lead)
            if not db_lead.whatsapp_draft:
                db_lead.whatsapp_draft = whatsapp_gen.generate(db_lead)
            if not db_lead.call_script:
                db_lead.call_script = call_script_gen.generate(db_lead)
            if not db_lead.meeting_points:
                db_lead.meeting_points = meeting_points_gen.generate(db_lead)
            
            session.commit()
            logger.info(f"Sales package generated for {db_lead.business_name}")
            
            self.after(0, lambda: toast_manager.show(f"Sales package ready for {db_lead.business_name}!", "success"))
            self.after(0, self.load_leads)
        except Exception as e:
            logger.error(f"Failed to generate sales package: {e}")
            self.after(0, lambda: toast_manager.show(f"Error: {e}", "error"))
            session.rollback()
        finally:
            session.close()

    def export_csv(self):
        filepath = Exporter().export_csv()
        if filepath: os.startfile(os.path.dirname(filepath))
        
    def export_excel(self):
        filepath = Exporter().export_excel()
        if filepath: os.startfile(os.path.dirname(filepath))
        
    def export_pdf(self):
        filepath = Exporter().export_pdf()
        if filepath: os.startfile(os.path.dirname(filepath))


# ═══════════════════════════════════════════════════════════════
# Lead Details Modal
# ═══════════════════════════════════════════════════════════════

class LeadDetailsModal(ctk.CTkToplevel):
    def __init__(self, master, lead, **kwargs):
        super().__init__(master, **kwargs)
        self.lead = lead
        self.title(f"Opportunity — {lead.business_name}")
        self.geometry("1000x750")
        self.configure(fg_color=COLORS["background"])
        
        # Center Window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.grab_set()
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ── Header ────────────────────────────────────────
        header_frame = ctk.CTkFrame(
            self, fg_color=COLORS["surface"],
            corner_radius=0,
            border_width=0
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=SPACING["xl"], pady=SPACING["lg"])
        
        ctk.CTkLabel(
            header_content, text=lead.business_name,
            font=FONTS["heading1"], text_color=COLORS["text"]
        ).pack(anchor="w")
        
        # Score + Value row
        meta_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        meta_frame.pack(anchor="w", pady=(SPACING["sm"], 0))
        
        score = lead.opportunity_score or 0
        score_color = COLORS["success"] if score >= 60 else COLORS["warning"] if score >= 30 else COLORS["text_muted"]
        
        ctk.CTkLabel(
            meta_frame, text=f"Score: {score}/100",
            font=FONTS["heading3"], text_color=score_color
        ).pack(side="left", padx=(0, SPACING["lg"]))
        
        if lead.estimated_value:
            ctk.CTkLabel(
                meta_frame,
                text=f"Est. Value: ₹{lead.estimated_value:,.0f}",
                font=FONTS["heading3"], text_color=COLORS["success"]
            ).pack(side="left", padx=(0, SPACING["lg"]))
            
        ctk.CTkLabel(
            meta_frame,
            text=f"Status: {lead.status or 'Discovery'}",
            font=FONTS["heading3"], text_color=COLORS["text_muted"]
        ).pack(side="left")
        
        # ── Tabview ───────────────────────────────────────
        self.tabview = ctk.CTkTabview(
            self, fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            segmented_button_fg_color=COLORS["surface_light"],
            segmented_button_selected_color=COLORS["primary_muted"],
            segmented_button_selected_hover_color=COLORS["primary_muted"],
            segmented_button_unselected_color=COLORS["surface_light"],
            segmented_button_unselected_hover_color=COLORS["surface_elevated"]
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=SPACING["xl"], pady=SPACING["lg"])
        
        self.tabview.add("Analysis")
        self.tabview.add("Proposal")
        self.tabview.add("Email")
        self.tabview.add("WhatsApp")
        self.tabview.add("Call Script")
        self.tabview.add("Meeting")
        self.tabview.add("ROI Calculator")
        
        # Analysis Tab
        analysis_frame = ctk.CTkScrollableFrame(self.tabview.tab("Analysis"), fg_color="transparent")
        analysis_frame.pack(fill="both", expand=True)
        
        summary_text = lead.ai_summary or "Generate a Sales Package first to see the analysis."
        ctk.CTkLabel(
            analysis_frame, text=summary_text,
            font=FONTS["body"], text_color=COLORS["text_secondary"],
            justify="left", wraplength=850
        ).pack(pady=SPACING["md"], padx=SPACING["md"], anchor="nw")
        
        # Add visual screenshot previews if they exist
        from pathlib import Path
        from PIL import Image
        
        screenshots_dir = Path(lead.screenshot_path).parent if lead.screenshot_path else None
        if screenshots_dir:
            desktop_path = screenshots_dir / f"{lead.id}_desktop.png"
            mobile_path = screenshots_dir / f"{lead.id}_mobile.png"
            
            images_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
            images_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["lg"], anchor="nw")
            
            # Load and display desktop preview
            if desktop_path.exists():
                try:
                    img_desktop = Image.open(desktop_path)
                    w, h = img_desktop.size
                    new_h = int((400 / w) * h)
                    new_h = min(250, new_h)
                    
                    ctk_img_desktop = ctk.CTkImage(light_image=img_desktop, dark_image=img_desktop, size=(400, new_h))
                    
                    desktop_container = ctk.CTkFrame(images_frame, fg_color=COLORS["surface_light"], corner_radius=RADIUS["md"], border_width=1, border_color=COLORS["border"])
                    desktop_container.pack(side="left", padx=(0, SPACING["lg"]))
                    
                    ctk.CTkLabel(desktop_container, text="DESKTOP PREVIEW", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(pady=SPACING["xs"], padx=SPACING["sm"])
                    ctk.CTkLabel(desktop_container, image=ctk_img_desktop, text="").pack(padx=SPACING["sm"], pady=(0, SPACING["sm"]))
                except Exception as ex:
                    logger.error(f"Failed to render desktop screenshot preview: {ex}")
                    
            # Load and display mobile preview
            if mobile_path.exists():
                try:
                    img_mobile = Image.open(mobile_path)
                    w, h = img_mobile.size
                    new_h = int((120 / w) * h)
                    new_h = min(250, new_h)
                    
                    ctk_img_mobile = ctk.CTkImage(light_image=img_mobile, dark_image=img_mobile, size=(120, new_h))
                    
                    mobile_container = ctk.CTkFrame(images_frame, fg_color=COLORS["surface_light"], corner_radius=RADIUS["md"], border_width=1, border_color=COLORS["border"])
                    mobile_container.pack(side="left")
                    
                    ctk.CTkLabel(mobile_container, text="MOBILE PREVIEW", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(pady=SPACING["xs"], padx=SPACING["sm"])
                    ctk.CTkLabel(mobile_container, image=ctk_img_mobile, text="").pack(padx=SPACING["sm"], pady=(0, SPACING["sm"]))
                except Exception as ex:
                    logger.error(f"Failed to render mobile screenshot preview: {ex}")
        
        # Helper for basic text tabs
        def create_textbox(parent, text_content):
            tb = ctk.CTkTextbox(
                parent, font=FONTS["body"], wrap="word",
                fg_color=COLORS["surface_light"],
                text_color=COLORS["text_secondary"],
                corner_radius=RADIUS["md"],
                border_width=1, border_color=COLORS["border"]
            )
            tb.pack(fill="both", expand=True, padx=SPACING["md"], pady=(SPACING["md"], 0))
            tb.insert("1.0", text_content or "Generate a Sales Package first to populate this section.")
            tb.configure(state="disabled")
            return tb
            
        create_textbox(self.tabview.tab("Proposal"), lead.proposal)
        
        # Email Tab with Send Button
        create_textbox(self.tabview.tab("Email"), lead.email_draft)
        ctk.CTkButton(
            self.tabview.tab("Email"), text="Send via Default Mail Client",
            font=FONTS["body"], fg_color=COLORS["primary"], text_color=COLORS["background"],
            hover_color=COLORS["primary_muted"], corner_radius=RADIUS["sm"],
            command=self.send_email
        ).pack(pady=SPACING["md"], padx=SPACING["md"], anchor="e")
        
        # WhatsApp Tab with Send Button
        create_textbox(self.tabview.tab("WhatsApp"), lead.whatsapp_draft)
        ctk.CTkButton(
            self.tabview.tab("WhatsApp"), text="Send via WhatsApp Web",
            font=FONTS["body"], fg_color="#25D366", text_color=COLORS["background"],
            hover_color="#128C7E", corner_radius=RADIUS["sm"],
            command=self.send_whatsapp
        ).pack(pady=SPACING["md"], padx=SPACING["md"], anchor="e")
        
        create_textbox(self.tabview.tab("Call Script"), lead.call_script)
        create_textbox(self.tabview.tab("Meeting"), lead.meeting_points)
        
        # ROI Calculator Tab
        self._build_roi_calculator(self.tabview.tab("ROI Calculator"))

    def send_email(self):
        email = self.lead.email or "contact@example.com"
        subject = urllib.parse.quote(f"Website Opportunity for {self.lead.business_name}")
        body = urllib.parse.quote(self.lead.email_draft or "")
        
        # Auto-track outreach in pipeline
        import datetime
        update_lead(self.lead.id, {
            "status": "Proposal",
            "last_contacted": datetime.datetime.utcnow()
        })
        if hasattr(self.master, "load_leads"):
            self.master.load_leads()
        toast_manager.show("Outreach tracked. Moved to Proposal stage.", "success")
        
        webbrowser.open(f"mailto:{email}?subject={subject}&body={body}")

    def send_whatsapp(self):
        phone = self.lead.phone or ""
        phone = "".join(filter(str.isdigit, phone))
        text = urllib.parse.quote(self.lead.whatsapp_draft or "")
        
        # Auto-track outreach in pipeline
        import datetime
        update_lead(self.lead.id, {
            "status": "Proposal",
            "last_contacted": datetime.datetime.utcnow()
        })
        if hasattr(self.master, "load_leads"):
            self.master.load_leads()
        toast_manager.show("Outreach tracked. Moved to Proposal stage.", "success")
        
        webbrowser.open(f"https://wa.me/{phone}?text={text}")
        
    def _build_roi_calculator(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING["2xl"], pady=SPACING["2xl"])
        
        ctk.CTkLabel(
            container, text="ROI & Value Projection",
            font=FONTS["heading1"], text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, SPACING["xl"]))
        
        # Inputs Frame
        inputs_frame = ctk.CTkFrame(container, fg_color=COLORS["surface_light"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"])
        inputs_frame.pack(fill="x", pady=(0, SPACING["xl"]))
        
        # Avg Customer Value
        ctk.CTkLabel(inputs_frame, text="Average Customer Value ($)", font=FONTS["body"]).grid(row=0, column=0, padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["xs"]), sticky="w")
        self.val_var = ctk.IntVar(value=100)
        val_slider = ctk.CTkSlider(inputs_frame, from_=10, to=1000, variable=self.val_var, command=self._update_roi)
        val_slider.grid(row=1, column=0, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="ew")
        self.val_lbl = ctk.CTkLabel(inputs_frame, text="$100", font=FONTS["heading3"], text_color=COLORS["primary"])
        self.val_lbl.grid(row=1, column=1, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="w")
        
        # New Monthly Customers
        ctk.CTkLabel(inputs_frame, text="New Monthly Customers from Website", font=FONTS["body"]).grid(row=2, column=0, padx=SPACING["lg"], pady=(SPACING["xs"]), sticky="w")
        self.cust_var = ctk.IntVar(value=10)
        cust_slider = ctk.CTkSlider(inputs_frame, from_=1, to=100, variable=self.cust_var, command=self._update_roi)
        cust_slider.grid(row=3, column=0, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="ew")
        self.cust_lbl = ctk.CTkLabel(inputs_frame, text="10", font=FONTS["heading3"], text_color=COLORS["primary"])
        self.cust_lbl.grid(row=3, column=1, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="w")
        
        # Website Cost
        ctk.CTkLabel(inputs_frame, text="Your Website Fee ($)", font=FONTS["body"]).grid(row=4, column=0, padx=SPACING["lg"], pady=(SPACING["xs"]), sticky="w")
        self.cost_var = ctk.IntVar(value=1500)
        cost_slider = ctk.CTkSlider(inputs_frame, from_=100, to=10000, variable=self.cost_var, command=self._update_roi)
        cost_slider.grid(row=5, column=0, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="ew")
        self.cost_lbl = ctk.CTkLabel(inputs_frame, text="$1,500", font=FONTS["heading3"], text_color=COLORS["danger"])
        self.cost_lbl.grid(row=5, column=1, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="w")
        
        inputs_frame.columnconfigure(0, weight=1)
        
        # Results Frame
        res_frame = ctk.CTkFrame(container, fg_color=COLORS["surface_elevated"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"])
        res_frame.pack(fill="x")
        
        self.monthly_rev_lbl = ctk.CTkLabel(res_frame, text="Projected Monthly Revenue: $1,000", font=FONTS["heading2"], text_color=COLORS["success"])
        self.monthly_rev_lbl.pack(pady=(SPACING["xl"], SPACING["xs"]))
        
        self.yearly_rev_lbl = ctk.CTkLabel(res_frame, text="Projected Yearly Revenue: $12,000", font=FONTS["heading1"], text_color=COLORS["success"])
        self.yearly_rev_lbl.pack(pady=(0, SPACING["xs"]))
        
        self.roi_months_lbl = ctk.CTkLabel(res_frame, text="Website pays for itself in: 1.5 months", font=FONTS["heading3"], text_color=COLORS["text_secondary"])
        self.roi_months_lbl.pack(pady=(0, SPACING["xl"]))
        
        self._update_roi(None)

    def _update_roi(self, _):
        val = self.val_var.get()
        cust = self.cust_var.get()
        cost = self.cost_var.get()
        
        self.val_lbl.configure(text=f"${val:,}")
        self.cust_lbl.configure(text=f"{cust}")
        self.cost_lbl.configure(text=f"${cost:,}")
        
        monthly = val * cust
        yearly = monthly * 12
        months_to_roi = cost / monthly if monthly > 0 else 0
        
        self.monthly_rev_lbl.configure(text=f"Projected Monthly Revenue: ${monthly:,}")
        self.yearly_rev_lbl.configure(text=f"Projected Yearly Revenue: ${yearly:,}")
        self.roi_months_lbl.configure(text=f"Website pays for itself in: {months_to_roi:.1f} months")
