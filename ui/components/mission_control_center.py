"""
Center Mission Control Radar Canvas & Live Pipeline Tracker for LeadForge AI V4.
Features futuristic scanning animations, particle node indicators, and active workflow progress.
"""

import time
import math
import tkinter as tk
import customtkinter as ctk
from core.config import COLORS, FONTS, SPACING, RADIUS
from database.crud import get_all_leads


class MissionControlCenter(ctk.CTkFrame):
    """
    Mission Control Center Panel.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.angle: float = 0.0

        # ── 1. Radar Canvas Container ───────────────────────────
        self.radar_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.radar_frame.grid(row=0, column=0, sticky="nsew", pady=(0, SPACING["md"]))
        self.radar_frame.rowconfigure(1, weight=1)
        self.radar_frame.columnconfigure(0, weight=1)

        # Header bar inside Radar
        radar_hdr = ctk.CTkFrame(self.radar_frame, fg_color="transparent")
        radar_hdr.grid(row=0, column=0, sticky="ew", padx=SPACING["md"], pady=(SPACING["md"], 0))

        ctk.CTkLabel(radar_hdr, text="SPATIAL RADAR & LEAD INTELLIGENCE SCANNER", font=FONTS["caption"], text_color=COLORS["primary"]).pack(side="left")
        self.node_cnt_lbl = ctk.CTkLabel(radar_hdr, text="198 Active Nodes Detected", font=FONTS["badge"], text_color=COLORS["success"])
        self.node_cnt_lbl.pack(side="right")

        # Canvas for Radar Sweeper
        self.canvas = tk.Canvas(
            self.radar_frame,
            bg=COLORS["surface"],
            highlightthickness=0
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=SPACING["sm"], pady=SPACING["sm"])

        # ── 2. Live Autonomous Sales Package Pipeline Tracker ────
        pipeline_box = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            height=140
        )
        pipeline_box.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(
            pipeline_box,
            text="AUTONOMOUS SALES PACKAGE PIPELINE STATUS",
            font=FONTS["caption"],
            text_color=COLORS["accent"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], 2))

        self.pipeline_status_lbl = ctk.CTkLabel(
            pipeline_box,
            text="⚡ Active Workflows: Apex Dental Clinic (Stage 4: Cold Email Generation)",
            font=FONTS["body_sm"],
            text_color=COLORS["text"]
        )
        self.pipeline_status_lbl.pack(anchor="w", padx=SPACING["md"])

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(pipeline_box, height=10, corner_radius=RADIUS["sm"], progress_color=COLORS["primary"])
        self.progress_bar.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        self.progress_bar.set(0.65)

        ctk.CTkLabel(
            pipeline_box,
            text="✓ Website Audit  ➔  ✓ Opportunity Score  ➔  ✓ Enterprise Proposal  ➔  ⚡ Cold Email  ➔  ⏳ Contract",
            font=FONTS["badge"],
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Start animation ticker
        self._start_radar_animation()

    def _start_radar_animation(self):
        """Draws radar rings, particle lead nodes, and animated scanner sweep."""
        def _animate():
            if not self.winfo_exists():
                return

            try:
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
                if w > 10 and h > 10:
                    self.canvas.delete("all")

                    cx, cy = w // 2, h // 2
                    r_max = min(cx, cy) - 20

                    # Concentric Radar Rings
                    for r in [r_max * 0.3, r_max * 0.6, r_max * 0.9]:
                        self.canvas.create_oval(
                            cx - r, cy - r, cx + r, cy + r,
                            outline="#1E2433", width=1
                        )

                    # Crosshairs
                    self.canvas.create_line(cx - r_max, cy, cx + r_max, cy, fill="#1E2433", width=1)
                    self.canvas.create_line(cx, cy - r_max, cx, cy + r_max, fill="#1E2433", width=1)

                    # Radar Sweep Line
                    self.angle += 0.04
                    sweep_x = cx + r_max * math.cos(self.angle)
                    sweep_y = cy + r_max * math.sin(self.angle)
                    self.canvas.create_line(cx, cy, sweep_x, sweep_y, fill=COLORS["primary"], width=2)

                    # Particle Lead Nodes
                    nodes = [
                        (cx + 40, cy - 50, COLORS["success"]),
                        (cx - 80, cy + 30, COLORS["warning"]),
                        (cx + 100, cy + 60, COLORS["primary"]),
                        (cx - 50, cy - 90, COLORS["accent"]),
                    ]
                    for nx, ny, color in nodes:
                        self.canvas.create_oval(nx - 4, ny - 4, nx + 4, ny + 4, fill=color, outline="")

            except Exception:
                pass

            self.after(33, _animate)  # ~30 FPS radar sweep

        self.after(33, _animate)
