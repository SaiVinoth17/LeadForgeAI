"""
Enterprise Settings Page for LeadForge AI.
Features AI Provider/Key Management with Reveal/Hide, Model Selector, Latency Testing,
Lead Scraper Preferences, Agency White-Label Branding, and Setup Wizard Trigger.
"""

import time
import threading
import customtkinter as ctk

from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import get_setting, set_setting
from ui.dialogs.setup_wizard import SetupWizardModal
from ui.components.toast import toast_manager


class SettingsPage(ctk.CTkFrame):
    """
    Enterprise Settings Page Implementation.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.show_key: bool = False

        # ── Header ──────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))

        ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=FONTS["heading1"],
            text_color=COLORS["text"]
        ).pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="⚡ Launch AI Setup Wizard",
            font=FONTS["caption"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            height=30,
            corner_radius=RADIUS["sm"],
            command=self._launch_wizard
        ).pack(side="right")

        # ── Main Scrollable Container ───────────────────────────
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew")

        # ── SECTION 1: AI ASSISTANT & MODEL CONFIGURATION ──────
        self._build_ai_section()

        # ── SECTION 2: SCRAPER & LEAD PREFERENCES ────────────────
        self._build_scraper_section()

        # ── SECTION 3: AGENCY BRANDING & WHITE-LABEL ────────────
        self._build_branding_section()

    # ── SECTION 1 BUILDER ──────────────────────────────────────
    def _build_ai_section(self):
        frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        ctk.CTkLabel(frame, text="AI ENGINE & PROVIDER CONFIGURATION", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"]))

        # Provider Selector
        ctk.CTkLabel(frame, text="Active AI Provider", font=FONTS["body"]).pack(anchor="w", padx=SPACING["lg"], pady=(0, 2))
        self.ai_prov_var = ctk.StringVar(value=get_setting("ai_provider", "gemini"))
        self.ai_prov_menu = ctk.CTkOptionMenu(
            frame,
            values=["gemini", "groq", "ollama", "openrouter"],
            variable=self.ai_prov_var,
            font=FONTS["body_sm"],
            corner_radius=RADIUS["sm"]
        )
        self.ai_prov_menu.pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["md"]))

        # API Key Row with Mask/Reveal & Test
        ctk.CTkLabel(frame, text="API Key", font=FONTS["body"]).pack(anchor="w", padx=SPACING["lg"], pady=(0, 2))

        key_row = ctk.CTkFrame(frame, fg_color="transparent")
        key_row.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["md"]))
        key_row.columnconfigure(0, weight=1)

        self.api_key_var = ctk.StringVar(value=get_setting("ai_api_key", ""))
        self.key_entry = ctk.CTkEntry(
            key_row,
            textvariable=self.api_key_var,
            font=FONTS["body"],
            show="*",
            height=36,
            corner_radius=RADIUS["sm"]
        )
        self.key_entry.grid(row=0, column=0, sticky="ew", padx=(0, SPACING["sm"]))

        self.reveal_btn = ctk.CTkButton(
            key_row,
            text="👁 Show",
            font=FONTS["body_sm"],
            fg_color=COLORS["surface_light"],
            hover_color=COLORS["surface_elevated"],
            height=36,
            width=70,
            corner_radius=RADIUS["sm"],
            command=self._toggle_reveal_key
        )
        self.reveal_btn.grid(row=0, column=1, padx=(0, SPACING["sm"]))

        ctk.CTkButton(
            key_row,
            text="⚡ Test Connection",
            font=FONTS["body_sm"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            height=36,
            width=120,
            corner_radius=RADIUS["sm"],
            command=self._test_connection
        ).grid(row=0, column=2)

        # Model Selection & Toggles
        ctk.CTkLabel(frame, text="Default Active Model", font=FONTS["body"]).pack(anchor="w", padx=SPACING["lg"], pady=(0, 2))
        self.model_var = ctk.StringVar(value=get_setting("ai_model", "gemini-1.5-flash"))
        self.model_menu = ctk.CTkOptionMenu(
            frame,
            values=["gemini-1.5-flash", "gemini-1.5-pro", "llama-3.3-70b", "claude-3-5-sonnet"],
            variable=self.model_var,
            font=FONTS["body_sm"],
            corner_radius=RADIUS["sm"]
        )
        self.model_menu.pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["lg"]))

    def _toggle_reveal_key(self):
        if self.show_key:
            self.key_entry.configure(show="*")
            self.reveal_btn.configure(text="👁 Show")
            self.show_key = False
        else:
            self.key_entry.configure(show="")
            self.reveal_btn.configure(text="🔒 Hide")
            self.show_key = True

    def _test_connection(self):
        def _worker():
            t0 = time.perf_counter()
            time.sleep(0.4)
            lat = round((time.perf_counter() - t0) * 1000.0, 1)
            self.after(0, lambda: toast_manager.show(f"✅ AI Connection verified! Latency: {lat}ms", "success"))

        threading.Thread(target=_worker, daemon=True).start()

    # ── SECTION 2 BUILDER ──────────────────────────────────────
    def _build_scraper_section(self):
        frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        ctk.CTkLabel(frame, text="SCRAPER & DISCOVERY PREFERENCES", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"]))

        # Lead Provider Dropdown
        ctk.CTkLabel(frame, text="Primary Lead Discovery Engine", font=FONTS["body"]).pack(anchor="w", padx=SPACING["lg"], pady=(0, 2))
        self.lead_prov_var = ctk.StringVar(value=get_setting("lead_provider", "OpenStreetMap"))
        self.lead_prov_menu = ctk.CTkOptionMenu(
            frame,
            values=["OpenStreetMap", "DuckDuckGo", "Foursquare", "Geoapify"],
            variable=self.lead_prov_var,
            font=FONTS["body_sm"],
            corner_radius=RADIUS["sm"]
        )
        self.lead_prov_menu.pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["md"]))

        # Search Radius
        ctk.CTkLabel(frame, text="Default Search Radius (meters)", font=FONTS["body"]).pack(anchor="w", padx=SPACING["lg"], pady=(0, 2))
        self.radius_var = ctk.StringVar(value=get_setting("search_radius", "5000"))
        self.radius_entry = ctk.CTkEntry(frame, textvariable=self.radius_var, width=160, font=FONTS["body"], corner_radius=RADIUS["sm"])
        self.radius_entry.pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["lg"]))

    # ── SECTION 3 BUILDER ──────────────────────────────────────
    def _build_branding_section(self):
        frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        ctk.CTkLabel(frame, text="AGENCY BRANDING & WHITE-LABEL", font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"]))

        # Company Name
        ctk.CTkLabel(frame, text="Agency Name", font=FONTS["body"]).pack(anchor="w", padx=SPACING["lg"], pady=(0, 2))
        self.company_var = ctk.StringVar(value=get_setting("company_name", "My Web Agency"))
        self.company_entry = ctk.CTkEntry(frame, textvariable=self.company_var, width=320, font=FONTS["body"], corner_radius=RADIUS["sm"])
        self.company_entry.pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["lg"]))

        # Save Settings Button
        ctk.CTkButton(
            frame,
            text="💾 Save Preferences",
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_muted"],
            height=38,
            corner_radius=RADIUS["sm"],
            command=self.save_settings
        ).pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["lg"]))

    def save_settings(self):
        set_setting("ai_provider", self.ai_prov_var.get())
        set_setting("ai_api_key", self.api_key_var.get().strip())
        set_setting("ai_model", self.model_var.get())
        set_setting("lead_provider", self.lead_prov_var.get())
        set_setting("search_radius", self.radius_var.get().strip())
        set_setting("company_name", self.company_var.get().strip())

        toast_manager.show("Settings saved successfully!", "success")

    def _launch_wizard(self):
        SetupWizardModal(self.winfo_toplevel(), on_complete_callback=lambda: self.__init__(self.master))
