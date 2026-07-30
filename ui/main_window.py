"""
Main Application Window Container for LeadForge AI.
Handles sidebar navigation, lazy page instantiation, and automatic AI Setup Wizard onboarding check.
"""

import customtkinter as ctk
from core.config import COLORS, SPACING
from core.events import event_bus, Events
from database.crud import get_setting
from ui.sidebar import Sidebar
from ui.pages.command_center import CommandCenterPage
from ui.pages.lead_generator import LeadGeneratorPage
from ui.pages.crm import CRMPage
from ui.pages.website_analyzer import WebsiteAnalyzerPage
from ui.pages.settings import SettingsPage
from ui.pages.map_view import MapViewPage
from ui.pages.proposal_generator import ProposalGeneratorPage
from ui.pages.ai_assistant import AIAssistantPage
from ui.dialogs.setup_wizard import SetupWizardModal
from ui.dialogs.boot_screen import ForgeOSBootScreen


class MainWindow(ctk.CTkFrame):
    """
    Main Application Window layout container.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content Area — generous padding for breathing room
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=SPACING["2xl"], pady=SPACING["xl"])
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(0, weight=1)

        # Initialize Pages
        self.pages = {}
        self._init_pages()

        # Event Listeners
        event_bus.subscribe(Events.NAVIGATE, self.show_page)

        # Show default page
        self.show_page("dashboard")

        # Check first-run onboarding status & trigger Forge OS Boot Screen
        self.after(200, self._check_first_run_onboarding)

    def _check_first_run_onboarding(self):
        """Launches Setup Wizard if AI setup unconfigured, otherwise launches Forge OS Boot Screen."""
        completed = get_setting("ai_setup_completed", "false")
        if completed != "true":
            SetupWizardModal(self.winfo_toplevel())
        else:
            ForgeOSBootScreen(self.winfo_toplevel())

    def _init_pages(self):
        # Store class references for lazy instantiation on first access
        self.page_classes = {
            "dashboard": CommandCenterPage,
            "lead_generator": LeadGeneratorPage,
            "crm": CRMPage,
            "analyzer": WebsiteAnalyzerPage,
            "map_view": MapViewPage,
            "proposals": ProposalGeneratorPage,
            "ai_assistant": AIAssistantPage,
            "settings": SettingsPage
        }

    def show_page(self, page_id: str):
        if page_id not in self.pages:
            # Lazy load the page
            page_class = self.page_classes.get(page_id)
            if page_class:
                self.pages[page_id] = page_class(self.content_area)
                self.pages[page_id].grid(row=0, column=0, sticky="nsew")

        page = self.pages.get(page_id)
        if page:
            page.tkraise()
            # Refresh data on activation
            if page_id == "dashboard" and hasattr(page, "refresh_dashboard"):
                page.refresh_dashboard()
            elif page_id == "crm":
                page.load_leads()
            elif page_id == "map_view":
                page.load_map()
            elif page_id == "proposals":
                page.load_leads()
