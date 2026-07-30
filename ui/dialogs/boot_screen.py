"""
FORGE OS V4 Premium Animated Boot Splash Window.
Displays a 2.5-second intentional startup sequence initializing AI agents, providers, and daily intelligence.
"""

import time
import threading
import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS


class ForgeOSBootScreen(ctk.CTkToplevel):
    """
    Futuristic Startup Boot Splash Sequence.
    """
    BOOT_STEPS = [
        "Initializing Forge OS Core...",
        "Loading Autonomous AI Workforce (8 Agents)...",
        "Connecting AI Provider Router (Gemini, Groq, Ollama)...",
        "Indexing Lead Intelligence & QuadTree GIS...",
        "Assembling Daily Intelligence Brief & Forecast...",
        "Mission Control Ready ✓"
    ]

    def __init__(self, master, on_ready_callback=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_ready_callback = on_ready_callback

        # Window Config
        self.title("Forge OS V4 — Initializing")
        self.geometry("560x360")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["background"])

        self.transient(master)
        self.grab_set()

        # Center Container
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["lg"], border_width=1, border_color=COLORS["primary"])
        container.grid(row=0, column=0, sticky="nsew", padx=SPACING["md"], pady=SPACING["md"])

        # Logo / Title Header
        ctk.CTkLabel(
            container,
            text="⚡ FORGE OS V4",
            font=FONTS["display"],
            text_color=COLORS["primary"]
        ).pack(anchor="center", pady=(SPACING["xl"], 2))

        ctk.CTkLabel(
            container,
            text="AUTONOMOUS AGENCY OPERATING SYSTEM",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="center", pady=(0, SPACING["lg"]))

        # Step Label
        self.step_label = ctk.CTkLabel(
            container,
            text="Initializing Forge OS Core...",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self.step_label.pack(anchor="center", pady=(0, SPACING["md"]))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            container,
            width=380,
            height=12,
            corner_radius=RADIUS["sm"],
            progress_color=COLORS["primary"]
        )
        self.progress_bar.pack(anchor="center", pady=(0, SPACING["lg"]))
        self.progress_bar.set(0.0)

        # Status Footer
        self.footer_lbl = ctk.CTkLabel(
            container,
            text="System Latency: 12ms | Security: Encrypted",
            font=FONTS["badge"],
            text_color=COLORS["text_tertiary"]
        )
        self.footer_lbl.pack(anchor="center")

        # Start background boot sequence
        threading.Thread(target=self._run_boot_sequence, daemon=True).start()

    def _run_boot_sequence(self):
        n_steps = len(self.BOOT_STEPS)
        for idx, step_text in enumerate(self.BOOT_STEPS):
            progress = (idx + 1) / n_steps
            time.sleep(0.35)  # Total 2.1s boot sequence
            self.after(0, self._update_progress, step_text, progress)

        time.sleep(0.4)
        self.after(0, self._finish_boot)

    def _update_progress(self, text: str, progress: float):
        if not self.winfo_exists():
            return
        self.step_label.configure(text=text)
        self.progress_bar.set(progress)

    def _finish_boot(self):
        if self.on_ready_callback:
            self.on_ready_callback()
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
