import customtkinter as ctk
import threading
from concurrent.futures import ThreadPoolExecutor
from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import add_lead, get_setting, db_manager
from services.analyzer import WebsiteAnalyzer, fast_analyze_lead
from core.logger import logger

class LeadGeneratorPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ── Header ────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["lg"]))
        
        ctk.CTkLabel(
            header_frame, text="Opportunity Finder",
            font=FONTS["heading1"], text_color=COLORS["text"]
        ).pack(side="left")
        
        # ── Main Layout: Left Panel + Right Results ───────
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew")
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
        # ── Left: Search Panel ────────────────────────────
        self.filter_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            width=300,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.filter_frame.grid(row=0, column=0, sticky="ns", padx=(0, SPACING["lg"]))
        
        # Search Parameters section
        ctk.CTkLabel(
            self.filter_frame, text="SEARCH PARAMETERS",
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(SPACING["lg"], SPACING["md"]), padx=SPACING["lg"])
        
        self.query_var = ctk.StringVar()
        self.location_var = ctk.StringVar()
        self.radius_var = ctk.StringVar(value="5000")
        
        self._add_filter_input("Business Category", "e.g. Plumber, Restaurant", self.query_var)
        self._add_filter_input("Location", "e.g. Mumbai, New York", self.location_var)
        self._add_filter_input("Search Radius (meters)", "5000", self.radius_var)
        
        # Filters section
        ctk.CTkLabel(
            self.filter_frame, text="OPPORTUNITY FILTERS",
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(SPACING["xl"], SPACING["md"]), padx=SPACING["lg"])
        
        self.filter_website = ctk.StringVar(value="Any")
        ctk.CTkLabel(
            self.filter_frame, text="Website Status",
            font=FONTS["small"], text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=SPACING["lg"])
        ctk.CTkOptionMenu(
            self.filter_frame, variable=self.filter_website,
            values=["Any", "No Website", "Facebook/Instagram Only", "Website Exists"],
            corner_radius=RADIUS["sm"],
            fg_color=COLORS["surface_light"],
            button_color=COLORS["surface_elevated"],
            button_hover_color=COLORS["border_light"]
        ).pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xs"], SPACING["md"]))
        
        self.filter_priority = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.filter_frame, text="High Opportunity Only",
            variable=self.filter_priority, font=FONTS["body"],
            corner_radius=RADIUS["sm"],
            border_color=COLORS["border_light"],
            hover_color=COLORS["surface_elevated"],
            fg_color=COLORS["primary"]
        ).pack(anchor="w", padx=SPACING["lg"], pady=SPACING["md"])
        
        # Search Button
        self.search_btn = ctk.CTkButton(
            self.filter_frame, text="Find Opportunities",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=48,
            font=FONTS["heading3"],
            corner_radius=RADIUS["md"],
            command=self.on_search
        )
        self.search_btn.pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xl"], SPACING["md"]))
        
        self.status_label = ctk.CTkLabel(
            self.filter_frame, text="",
            text_color=COLORS["text_muted"],
            font=FONTS["small"],
            wraplength=250
        )
        self.status_label.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
        
        # ── Right: Results Area ───────────────────────────
        self.results_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.results_frame.grid(row=0, column=1, sticky="nsew")
        
        # Empty state
        self._show_empty_state()
        
        # Thread pool for background analysis
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _show_empty_state(self):
        for w in self.results_frame.winfo_children():
            w.destroy()
        empty = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        empty.pack(expand=True, fill="both", pady=SPACING["3xl"])
        ctk.CTkLabel(
            empty, text="Ready to discover",
            font=FONTS["heading2"], text_color=COLORS["text_muted"]
        ).pack(pady=(SPACING["3xl"], SPACING["sm"]))
        ctk.CTkLabel(
            empty, text="Enter a business category and location to find\nbusinesses that need websites.",
            font=FONTS["body"], text_color=COLORS["text_tertiary"],
            justify="center"
        ).pack()
        
    def _add_filter_input(self, label, placeholder, variable):
        ctk.CTkLabel(
            self.filter_frame, text=label,
            font=FONTS["small"], text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["xs"], 0))
        ctk.CTkEntry(
            self.filter_frame, textvariable=variable,
            placeholder_text=placeholder,
            corner_radius=RADIUS["sm"],
            fg_color=COLORS["surface_light"],
            border_color=COLORS["border"],
            border_width=1
        ).pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xs"], SPACING["sm"]))
        
    def on_search(self):
        query = self.query_var.get().strip()
        location = self.location_var.get().strip()
        
        if not query or not location:
            self.status_label.configure(text="Please enter Category and Location.", text_color=COLORS["danger"])
            return
            
        try:
            radius = int(self.radius_var.get().strip())
        except:
            radius = 5000
            
        self.search_btn.configure(state="disabled", text="Scanning Area...")
        self.status_label.configure(text="Fetching businesses from OpenStreetMap...", text_color=COLORS["text_secondary"])
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        threading.Thread(target=self._run_search, args=(query, location, radius), daemon=True).start()
        
    def _run_search(self, query, location, radius):
        from services.providers import OSMProvider
        
        service = OSMProvider()
        
        try:
            results = service.search_leads(query=query, location=location, radius=radius)
        except Exception as e:
            if str(e) == "ALL_SERVERS_UNAVAILABLE":
                self.after(0, lambda: self.status_label.configure(text="All OpenStreetMap Overpass servers are currently unavailable.\nPlease try again later.", text_color=COLORS["danger"]))
            else:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {e}", text_color=COLORS["danger"]))
            self.after(0, lambda: self.search_btn.configure(state="normal", text="Find Opportunities"))
            return
            
        if not results:
            self.after(0, lambda: self.status_label.configure(text="No businesses matched your filters in this area.", text_color=COLORS["warning"]))
            self.after(0, lambda: self.search_btn.configure(state="normal", text="Find Opportunities"))
            return
            
        # Filter and Score Leads locally before import
        filtered_results = []
        for res in results:
            fast_metrics = fast_analyze_lead(res)
            w_type = fast_metrics["website_type"]
            score = fast_metrics["opportunity_score"]
            
            f_web = self.filter_website.get()
            if f_web == "No Website" and w_type != "None": continue
            if f_web == "Facebook/Instagram Only" and w_type not in ["Facebook", "Instagram"]: continue
            if f_web == "Website Exists" and w_type == "None": continue
            
            if self.filter_priority.get() and score < 40:
                continue
                
            res.update(fast_metrics)
            filtered_results.append(res)
            
        if not filtered_results:
            self.after(0, lambda: self.status_label.configure(text="No businesses matched your strict opportunity filters.", text_color=COLORS["warning"]))
            self.after(0, lambda: self.search_btn.configure(state="normal", text="Find Opportunities"))
            return
            
        self.after(0, lambda: self.status_label.configure(text=f"Importing {len(filtered_results)} opportunities...", text_color=COLORS["primary"]))
        
        imported_count = 0
        total_website_opps = 0
        total_facebook_only = 0
        total_instagram_only = 0
        total_prof = 0
        sum_score = 0
        sum_revenue = 0
        
        added_leads = []
        for i, res in enumerate(filtered_results):
            lead_data = {
                "business_name": res.get("business_name", "Unknown"),
                "address": res.get("address"),
                "phone": res.get("phone"),
                "website": res.get("website"),
                "email": res.get("email"),
                "osm_id": res.get("osm_id"),
                "latitude": res.get("latitude"),
                "longitude": res.get("longitude"),
                "provider": "OpenStreetMap",
                "city": res.get("city", location),
                "category": query,
                "website_type": res.get("website_type"),
                "has_professional_email": res.get("has_professional_email"),
                "opportunity_score": res.get("opportunity_score")
            }
            lead = add_lead(lead_data)
            if lead:
                imported_count += 1
                sum_score += lead.opportunity_score or 0
                
                rev = 0
                wt = lead.website_type
                if wt in ["None", "Facebook", "Instagram", "WhatsApp"]:
                    rev = 45000 if "restaurant" in query.lower() or "cafe" in query.lower() else 65000 if "hotel" in query.lower() else 35000
                    total_website_opps += 1
                else:
                    rev = 25000
                    total_prof += 1
                    
                if wt == "Facebook": total_facebook_only += 1
                if wt == "Instagram": total_instagram_only += 1
                sum_revenue += rev
                
                added_leads.append(lead)
                self.executor.submit(self._background_analyze, lead.id)
                
        # Render Search Summary First
        avg_score = int(sum_score / imported_count) if imported_count > 0 else 0
        summary_data = {
            "query": query, "location": location,
            "found": len(results), "imported": imported_count,
            "opps": total_website_opps, "prof": total_prof,
            "fb": total_facebook_only, "ig": total_instagram_only,
            "avg_score": avg_score, "rev": sum_revenue
        }
        self.after(0, lambda: self._render_search_summary(summary_data))
        
        # Then render cards
        for i, lead in enumerate(added_leads):
            self.after(0, lambda l=lead, row=i: self._add_result_card(l, row))
                
        self.after(0, lambda: self.status_label.configure(text=f"Found {imported_count} new opportunities!", text_color=COLORS["success"]))
        self.after(0, lambda: self.search_btn.configure(state="normal", text="Find Opportunities"))

    def _render_search_summary(self, data):
        summary_frame = ctk.CTkFrame(
            self.results_frame,
            fg_color=COLORS["surface_light"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["primary_muted"]
        )
        summary_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["lg"]))
        
        # Header
        ctk.CTkLabel(
            summary_frame,
            text=f"SEARCH RESULTS — {data['query'].upper()} IN {data['location'].upper()}",
            font=FONTS["caption"], text_color=COLORS["primary"]
        ).pack(pady=(SPACING["md"], SPACING["sm"]), padx=SPACING["lg"], anchor="w")
        
        # Stats grid
        grid_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["md"]))
        
        def add_stat(row, col, label, value, color=COLORS["text_secondary"]):
            ctk.CTkLabel(
                grid_frame, text=label,
                font=FONTS["small"], text_color=COLORS["text_muted"]
            ).grid(row=row, column=col*2, sticky="w", padx=(0, SPACING["xs"]), pady=2)
            ctk.CTkLabel(
                grid_frame, text=str(value),
                font=FONTS["heading3"], text_color=color
            ).grid(row=row, column=col*2+1, sticky="w", padx=(0, SPACING["xl"]), pady=2)
            
        add_stat(0, 0, "Found",         data['found'])
        add_stat(1, 0, "Opportunities",  data['opps'],       COLORS["warning"])
        add_stat(2, 0, "Professional",   data['prof'])
        add_stat(0, 1, "Facebook Only",  data['fb'])
        add_stat(1, 1, "Instagram Only", data['ig'])
        add_stat(0, 2, "Avg Score",      f"{data['avg_score']}/100", COLORS["primary"])
        add_stat(1, 2, "Est. Revenue",   f"₹{data['rev']:,.0f}",    COLORS["success"])

    def _background_analyze(self, lead_id):
        session = db_manager.get_session()
        try:
            from models.lead import Lead
            from services.ai_generators import proposal_gen, email_gen, whatsapp_gen, call_script_gen, meeting_points_gen
            
            lead = session.query(Lead).filter(Lead.id == lead_id).first()
            if not lead: return
            
            analyzer = WebsiteAnalyzer(lead)
            res = analyzer.run_analysis()
            
            lead.has_ssl = res["has_ssl"]
            lead.is_mobile_responsive = res["is_mobile_responsive"]
            lead.has_online_booking = res["has_online_booking"]
            lead.has_logo = res["has_logo"]
            lead.opportunity_score = res["opportunity_score"]
            lead.priority = res["lead_priority"]
            lead.ai_summary = res["ai_summary"]
            lead.estimated_value = res["estimated_value"]
            
            # Auto-generate outreach drafts and proposal immediately
            if not lead.proposal:
                lead.proposal = proposal_gen.generate(lead)
            if not lead.email_draft:
                lead.email_draft = email_gen.generate(lead)
            if not lead.whatsapp_draft:
                lead.whatsapp_draft = whatsapp_gen.generate(lead)
            if not lead.call_script:
                lead.call_script = call_script_gen.generate(lead)
            if not lead.meeting_points:
                lead.meeting_points = meeting_points_gen.generate(lead)
                
            session.commit()
            logger.info(f"Auto-generated sales package in background for lead {lead_id}")
        except Exception as e:
            logger.error(f"Background analysis failed for lead {lead_id}: {e}")
            session.rollback()
        finally:
            session.close()
            
    def _add_result_card(self, lead, row):
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=COLORS["surface_light"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])
        card.columnconfigure(1, weight=1)
        
        # Opportunity badge
        is_opp = lead.website_type in ["None", "Facebook", "Instagram"]
        badge_fg = COLORS["primary_muted"] if is_opp else COLORS["surface_elevated"]
        badge_text_color = COLORS["primary"] if is_opp else COLORS["text_muted"]
        badge_text = "OPPORTUNITY" if is_opp else "HAS WEBSITE"
        
        ctk.CTkLabel(
            card, text=badge_text,
            font=FONTS["badge"],
            fg_color=badge_fg,
            text_color=badge_text_color,
            corner_radius=RADIUS["sm"],
            padx=10, pady=3
        ).grid(row=0, column=0, sticky="nw", padx=SPACING["md"], pady=SPACING["md"])
        
        # Details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="w", padx=SPACING["sm"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            details_frame, text=lead.business_name,
            font=FONTS["heading3"], text_color=COLORS["text"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            details_frame,
            text=f"{lead.category}  ·  {lead.phone or 'No phone'}",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        
        # Score pill
        score = lead.opportunity_score or 0
        score_color = COLORS["success"] if score >= 60 else COLORS["warning"] if score >= 30 else COLORS["text_muted"]
        ctk.CTkLabel(
            card, text=f"{score}",
            font=FONTS["heading2"],
            text_color=score_color
        ).grid(row=0, column=2, sticky="ne", padx=SPACING["lg"], pady=SPACING["md"])
