import customtkinter as ctk
import threading
from core.config import COLORS, FONTS, SPACING, RADIUS
from services.analyzer import WebsiteAnalyzer

class WebsiteAnalyzerPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(self, text="Website Analyzer", font=FONTS["heading1"], text_color=COLORS["text"])
        self.header.grid(row=0, column=0, sticky="w", pady=(0, SPACING["xl"]))
        
        # Form
        self.form_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"])
        self.form_frame.grid(row=1, column=0, sticky="ew")
        
        self.url_var = ctk.StringVar()
        
        ctk.CTkLabel(self.form_frame, text="Website URL (e.g. example.com)", font=FONTS["body"]).grid(row=0, column=0, padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["xs"]), sticky="w")
        self.url_entry = ctk.CTkEntry(self.form_frame, textvariable=self.url_var, width=400, corner_radius=RADIUS["sm"])
        self.url_entry.grid(row=1, column=0, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="w")
        
        self.analyze_btn = ctk.CTkButton(self.form_frame, text="Analyze", command=self.on_analyze, corner_radius=RADIUS["sm"])
        self.analyze_btn.grid(row=1, column=1, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="w")
        
        self.status_label = ctk.CTkLabel(self.form_frame, text="", text_color=COLORS["text_muted"])
        self.status_label.grid(row=2, column=0, columnspan=2, padx=SPACING["lg"], pady=(0, SPACING["md"]), sticky="w")
        
        # Results
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["border"])
        self.results_frame.grid(row=2, column=0, sticky="nsew", pady=(SPACING["xl"], 0))
        self.results_frame.columnconfigure(1, weight=1)
        
    def on_analyze(self):
        url = self.url_var.get().strip()
        if not url:
            self.status_label.configure(text="Please enter a URL.", text_color=COLORS["danger"])
            return
            
        self.analyze_btn.configure(state="disabled", text="Analyzing...")
        self.status_label.configure(text="Fetching and analyzing website data...", text_color=COLORS["text"])
        
        # Clear previous
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        threading.Thread(target=self._run_analysis, args=(url,), daemon=True).start()
        
    def _run_analysis(self, url):
        analyzer = WebsiteAnalyzer(url)
        results = analyzer.run_analysis()
        
        self.after(0, lambda: self._display_results(results))
        self.after(0, lambda: self.analyze_btn.configure(state="normal", text="Analyze"))
        self.after(0, lambda: self.status_label.configure(text="Analysis complete.", text_color=COLORS["success"]))
        
    def _display_results(self, results):
        row = 0
        for key, val in results.items():
            if key in ["social_links", "emails", "detected_frameworks", "analytics_tags"]:
                val = ", ".join(val) if val else "None found"
            
            ctk.CTkLabel(self.results_frame, text=key.replace("_", " ").title() + ":", font=FONTS["heading3"]).grid(row=row, column=0, sticky="e", padx=SPACING["md"], pady=SPACING["md"])
            
            # Wrap text if summary
            if key == "ai_summary":
                lbl = ctk.CTkLabel(self.results_frame, text=val, font=FONTS["body"], wraplength=500, justify="left")
            else:
                lbl = ctk.CTkLabel(self.results_frame, text=str(val), font=FONTS["body"])
                
            lbl.grid(row=row, column=1, sticky="w", padx=SPACING["md"], pady=SPACING["md"])
            row += 1

