"""
Top Mission Control Header Navigation Bar for LeadForge AI V4.
"""

import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS
from ui.dialogs.command_palette import CommandPaletteModal


class MissionControlHeader(ctk.CTkFrame):
    """
    Futuristic Mission Control Header Widget.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.columnconfigure(1, weight=1)

        # ── Left: Status Badge ──────────────────────────────────
        left_box = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADIUS["sm"], border_width=1, border_color=COLORS["border"])
        left_box.grid(row=0, column=0, sticky="w", padx=(0, SPACING["md"]))

        status_lbl = ctk.CTkLabel(
            left_box,
            text="⚡ FORGE OS V4 ONLINE",
            font=FONTS["caption"],
            text_color=COLORS["primary"],
            padx=SPACING["sm"],
            pady=SPACING["3xs"]
        )
        status_lbl.pack()

        # ── Center: Search / Command Palette Bar ────────────────
        search_btn = ctk.CTkButton(
            self,
            text="🔍  Search leads or type 'Ctrl+K' for Command Palette...",
            font=FONTS["body_sm"],
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_light"],
            text_color=COLORS["text_muted"],
            anchor="w",
            height=36,
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            command=self._open_command_palette
        )
        search_btn.grid(row=0, column=1, sticky="ew", padx=SPACING["md"])

        # ── Right: AI Latency & Notifications ───────────────────
        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(
            right_box,
            text="🟢 Gemini 1.5 (12ms)",
            font=FONTS["badge"],
            text_color=COLORS["success"],
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["sm"],
            padx=SPACING["sm"],
            pady=SPACING["3xs"]
        ).pack(side="left", padx=SPACING["xs"])

        ctk.CTkButton(
            right_box,
            text="🔔 3",
            font=FONTS["caption"],
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_light"],
            text_color=COLORS["warning"],
            width=40,
            height=30,
            corner_radius=RADIUS["sm"]
        ).pack(side="left")

    def _open_command_palette(self):
        CommandPaletteModal(self.winfo_toplevel())
