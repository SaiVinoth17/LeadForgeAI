import customtkinter as ctk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import get_all_leads

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        
        self.refresh_dashboard()
        
    def refresh_dashboard(self):
        # Clear everything
        for widget in self.winfo_children():
            widget.destroy()
            
        self.leads = get_all_leads()
        total_leads = len(self.leads)
        
        # ── Greeting Header ───────────────────────────────
        import datetime
        hour = datetime.datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        today = datetime.datetime.now().date()
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["xl"]))
        
        ctk.CTkLabel(
            header_frame, text=f"{greeting}.",
            font=FONTS["heading1"], text_color=COLORS["text"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text=f"You have {total_leads} opportunities in your pipeline." if total_leads > 0 else "Start discovering website opportunities.",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(SPACING["xs"], 0))
        
        # ── Compute Metrics ───────────────────────────────
        website_opps = len([l for l in self.leads if getattr(l, "priority", "") in ["High Opportunity", "Medium"]])
        todays_leads = len([l for l in self.leads if l.created_date and l.created_date.date() == today])
        potential_revenue = sum([l.estimated_value or 0 for l in self.leads if l.status not in ["Won", "Lost"]])
        won = len([l for l in self.leads if l.status == "Won"])
        conversion = f"{(won/total_leads*100):.1f}%" if total_leads > 0 else "0%"
        
        opp_scores = [l.opportunity_score for l in self.leads if l.opportunity_score is not None]
        avg_opp_score = int(sum(opp_scores)/len(opp_scores)) if opp_scores else 0
        
        # ── Hero Metric Cards ─────────────────────────────
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["lg"]))
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        self._hero_card(metrics_frame, 0, "OPPORTUNITIES",  str(website_opps),                 COLORS["primary"])
        self._hero_card(metrics_frame, 1, "PIPELINE VALUE",  f"₹{potential_revenue:,.0f}",      COLORS["success"])
        self._hero_card(metrics_frame, 2, "AVG SCORE",       f"{avg_opp_score}",                COLORS["accent"])
        self._hero_card(metrics_frame, 3, "CONVERSION",      conversion,                        COLORS["warning"])
        
        # ── Secondary Metrics Row ─────────────────────────
        secondary_frame = ctk.CTkFrame(self, fg_color="transparent")
        secondary_frame.grid(row=2, column=0, sticky="ew", pady=(0, SPACING["lg"]))
        secondary_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        proposals = len([l for l in self.leads if l.status == "Proposal"])
        meetings = len([l for l in self.leads if l.status == "Meeting"])
        values = [l.estimated_value for l in self.leads if l.estimated_value]
        avg_value = int(sum(values)/len(values)) if values else 0
        
        self._stat_card(secondary_frame, 0, "Today's Discoveries", str(todays_leads))
        self._stat_card(secondary_frame, 1, "Proposals Sent",      str(proposals))
        self._stat_card(secondary_frame, 2, "Meetings",            str(meetings))
        self._stat_card(secondary_frame, 3, "Avg Project Value",   f"₹{avg_value:,.0f}")
        
        # ── Charts ────────────────────────────────────────
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.grid(row=3, column=0, sticky="nsew")
        
        if total_leads > 0:
            self._render_charts(charts_frame)
        else:
            # Onboarding Guide (Empty State)
            empty_frame = ctk.CTkFrame(charts_frame, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"])
            empty_frame.pack(fill="both", expand=True, padx=SPACING["sm"])
            
            content = ctk.CTkFrame(empty_frame, fg_color="transparent")
            content.place(relx=0.5, rely=0.5, anchor="center")
            
            ctk.CTkLabel(
                content, text="How to Land Your First Client",
                font=FONTS["heading1"], text_color=COLORS["text"]
            ).pack(pady=(0, SPACING["2xl"]))
            
            steps = [
                ("1. Discover", "Go to Opportunity Finder and search for a niche (e.g. 'Restaurant') in your city."),
                ("2. Analyze", "Click 'Generate Package' on a lead with a High Opportunity Score."),
                ("3. Pitch", "Use the 1-click 'Send Email' or 'Send WhatsApp' buttons to pitch the AI proposal.")
            ]
            
            for title, desc in steps:
                step_f = ctk.CTkFrame(content, fg_color=COLORS["surface_light"], corner_radius=RADIUS["md"])
                step_f.pack(fill="x", pady=SPACING["xs"])
                ctk.CTkLabel(step_f, text=title, font=FONTS["heading2"], text_color=COLORS["primary"]).pack(anchor="w", padx=SPACING["xl"], pady=(SPACING["md"], SPACING["xs"]))
                ctk.CTkLabel(step_f, text=desc, font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=SPACING["xl"], pady=(0, SPACING["md"]))

    def _hero_card(self, parent, col, label, value, accent_color):
        """Large hero metric card with colored left accent border."""
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1, border_color=COLORS["border"]
        )
        card.grid(row=0, column=col, sticky="ew", padx=SPACING["sm"], ipady=SPACING["sm"])
        
        # Accent bar (simulated with a small frame)
        accent = ctk.CTkFrame(card, fg_color=accent_color, width=4, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 0))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            content, text=label,
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            content, text=value,
            font=FONTS["metric"], text_color=COLORS["text"]
        ).pack(anchor="w", pady=(SPACING["xs"], 0))

    def _stat_card(self, parent, col, label, value):
        """Smaller secondary stat card."""
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1, border_color=COLORS["border"]
        )
        card.grid(row=0, column=col, sticky="ew", padx=SPACING["sm"])
        
        ctk.CTkLabel(
            card, text=label,
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        ).pack(pady=(SPACING["md"], SPACING["xs"]), padx=SPACING["lg"], anchor="w")
        
        ctk.CTkLabel(
            card, text=value,
            font=FONTS["heading2"], text_color=COLORS["text_secondary"]
        ).pack(pady=(0, SPACING["md"]), padx=SPACING["lg"], anchor="w")

    def _render_charts(self, parent):
        import threading
        
        # We need a copy of the leads data to pass to the thread safely
        leads_copy = list(self.leads)
        
        def build_chart():
            bg = COLORS["background"]
            text_c = COLORS["text_secondary"]
            muted_c = COLORS["text_muted"]
            grid_c = COLORS["border"]
            
            # Matplotlib isn't thread-safe for global style changes if done concurrently, 
            # but since only this thread builds the chart it should be fine.
            plt.style.use('dark_background')
            fig = plt.figure(figsize=(10, 4.5), facecolor=bg)
            fig.subplots_adjust(wspace=0.35)
            
            # ── Chart 1: Pipeline Funnel ──────────────────────
            ax1 = fig.add_subplot(121, facecolor=bg)
            pipeline_order = ["Discovery", "Qualified", "Proposal", "Meeting", "Negotiation", "Won"]
            pipeline_counts = {s: 0 for s in pipeline_order}
            for l in leads_copy:
                if l.status in pipeline_counts:
                    pipeline_counts[l.status] += 1
            
            bars = ax1.bar(
                pipeline_counts.keys(), pipeline_counts.values(),
                color=COLORS["primary_muted"], edgecolor=COLORS["primary"], linewidth=0.8
            )
            ax1.tick_params(axis='x', rotation=35, colors=muted_c, labelsize=9)
            ax1.tick_params(axis='y', colors=muted_c, labelsize=9)
            ax1.set_title("Sales Pipeline", color=text_c, fontsize=12, pad=12)
            for spine in ax1.spines.values():
                spine.set_visible(False)
            ax1.yaxis.grid(True, color=grid_c, alpha=0.3, linewidth=0.5)
            ax1.set_axisbelow(True)
    
            # ── Chart 2: Website Types ────────────────────────
            ax2 = fig.add_subplot(122, facecolor=bg)
            types = {"No Website": 0, "Facebook": 0, "Instagram": 0, "WhatsApp": 0, "Professional": 0}
            for l in leads_copy:
                wt = getattr(l, "website_type", "Unknown")
                if wt == "None":
                    types["No Website"] += 1
                elif wt in types:
                    types[wt] += 1
                else:
                    types["No Website"] += 1
                
            labels = [k for k, v in types.items() if v > 0]
            sizes = [v for v in types.values() if v > 0]
            chart_colors = ["#6366F1", "#A78BFA", "#34D399", "#FBBF24", "#F87171"]
            
            if sizes:
                wedges, texts, autotexts = ax2.pie(
                    sizes, labels=labels, autopct='%1.0f%%',
                    colors=chart_colors[:len(sizes)],
                    textprops={'color': muted_c, 'fontsize': 9},
                    wedgeprops={'linewidth': 1, 'edgecolor': bg},
                    pctdistance=0.75
                )
                for t in autotexts:
                    t.set_color(text_c)
                    t.set_fontsize(9)
            ax2.set_title("Opportunity Breakdown", color=text_c, fontsize=12, pad=12)
            
            fig.tight_layout(pad=2.0)
            
            # Post back to main thread
            self.after(0, self._embed_chart, fig, parent)

        # Start the background work
        threading.Thread(target=build_chart, daemon=True).start()

    def _embed_chart(self, fig, parent):
        # We must verify parent still exists (if user navigates away rapidly)
        if not parent.winfo_exists():
            plt.close(fig)
            return
            
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
