import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING
from core.events import event_bus, Events

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["sidebar_bg"], width=220, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # ── Brand Header ──────────────────────────────────
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.grid(row=0, column=0, sticky="ew", padx=SPACING["lg"], pady=(SPACING["xl"], SPACING["xs"]))
        
        # App name
        ctk.CTkLabel(
            brand_frame, text="LeadForge",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            brand_frame, text="AI",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["primary"]
        ).place(relx=0.55, rely=0.0)  # Inline "AI" colored
        
        # Tagline
        ctk.CTkLabel(
            brand_frame, text="Website Opportunity Intelligence",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))
        
        # Divider
        ctk.CTkFrame(self, fg_color=COLORS["divider"], height=1).grid(
            row=1, column=0, sticky="ew", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"])
        )
        
        # ── Navigation ────────────────────────────────────
        self.nav_buttons = []
        self.current_page = "dashboard"
        
        # DISCOVER section
        self._section_label("DISCOVER", 2)
        self._nav_button("◆  Dashboard",       3, "dashboard")
        self._nav_button("◎  Opportunity Finder", 4, "lead_generator")
        self._nav_button("▣  Pipeline",         5, "crm")
        
        # Divider
        ctk.CTkFrame(self, fg_color=COLORS["divider"], height=1).grid(
            row=6, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["sm"]
        )
        
        # ANALYZE section
        self._section_label("ANALYZE", 7)
        self._nav_button("◉  Website Analyzer", 8, "analyzer")
        self._nav_button("⊕  Map View",         9, "map_view")
        
        # Divider
        ctk.CTkFrame(self, fg_color=COLORS["divider"], height=1).grid(
            row=10, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["sm"]
        )
        
        # CREATE section
        self._section_label("CREATE", 11)
        self._nav_button("◈  Proposals",        12, "proposals")
        self._nav_button("◇  AI Assistant",     13, "ai_assistant")
        
        # Spacer
        self.grid_rowconfigure(14, weight=1)
        
        # Divider before bottom
        ctk.CTkFrame(self, fg_color=COLORS["divider"], height=1).grid(
            row=15, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["sm"]
        )
        
        # Bottom
        self._nav_button("⚙  Settings",        16, "settings")
        
        # Version badge
        ctk.CTkLabel(
            self, text="v2.0",
            font=FONTS["caption"],
            text_color=COLORS["text_tertiary"]
        ).grid(row=17, column=0, pady=(SPACING["sm"], SPACING["lg"]))
        
        self._update_button_styles()
        
    def _section_label(self, text, row):
        lbl = ctk.CTkLabel(
            self, text=text,
            font=FONTS["nav_section"],
            text_color=COLORS["sidebar_section"],
            anchor="w"
        )
        lbl.grid(row=row, column=0, sticky="ew", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["xs"]))
        
    def _nav_button(self, text, row, page_id):
        btn = ctk.CTkButton(
            self, text=text, font=FONTS["nav"],
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["surface_elevated"],
            anchor="w", height=36,
            corner_radius=SPACING["sm"],
            command=lambda p=page_id: self._on_nav_click(p)
        )
        btn.grid(row=row, column=0, sticky="ew", padx=SPACING["sm"], pady=2)
        self.nav_buttons.append((page_id, btn))
        
    def _on_nav_click(self, page_id):
        self.current_page = page_id
        self._update_button_styles()
        event_bus.emit(Events.NAVIGATE, page_id)
        
    def _update_button_styles(self):
        for pid, btn in self.nav_buttons:
            if pid == self.current_page:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color=COLORS["text"],
                    hover_color=COLORS["surface_elevated"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["surface_elevated"]
                )
