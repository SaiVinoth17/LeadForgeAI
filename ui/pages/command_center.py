"""
FORGE OS V6 — REACT 18 MISSION CONTROL DASHBOARD
Launches modular backend API server (backend.main:app) and loads the React 18 frontend web app.
"""

import os
import threading
import logging
import customtkinter as ctk
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
from backend.main import app as api_app
from core.logger import logger


def _run_api_server():
    """Background worker launching API server on port 49281."""
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        api_app.run(host="127.0.0.1", port=49281, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"API Server error: {e}")


class CommandCenterPage(ctk.CTkFrame):
    """
    FORGE OS V6 React Mission Control Page container with embedded WebView2.
    """
    _server_started = False

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack_propagate(False)

        if not CommandCenterPage._server_started:
            CommandCenterPage._server_started = True
            threading.Thread(target=_run_api_server, daemon=True).start()

        if not have_runtime():
            install_runtime()

        self.after(100, self._init_webview)

    def _init_webview(self):
        self.webview = WebView2(self, 1200, 800)
        self.webview.pack(fill="both", expand=True)

        app_url = "http://127.0.0.1:49281"
        self.after(200, lambda: self.webview.load_url(app_url))

    def refresh_dashboard(self):
        if hasattr(self, "webview"):
            app_url = "http://127.0.0.1:49281"
            self.webview.load_url(app_url)
