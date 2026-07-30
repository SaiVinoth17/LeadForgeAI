from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports_output"

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR, ASSETS_DIR, EXPORTS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Database
DB_PATH = DATA_DIR / "leadforge.db"

# UI Theme - Premium Dark Mode
THEME_COLOR = "dark-blue"  # CustomTkinter theme
APPEARANCE_MODE = "dark"

# ─── COLOR SYSTEM ─────────────────────────────────────────────
# Inspired by Linear, Arc Browser, Vercel — deep ink blacks with
# muted neon accents. Never harsh. Always sophisticated.
COLORS = {
    # Backgrounds — layered depth
    "background":       "#0A0C10",   # Deep ink black
    "surface":          "#12151C",   # Card / panel base
    "surface_light":    "#1A1E28",   # Elevated surface
    "surface_elevated": "#222838",   # Hover / active states
    "surface_glass":    "#161A24",   # Glassmorphism panels

    # Brand
    "primary":          "#6366F1",   # Indigo — premium, distinctive
    "primary_hover":    "#818CF8",   # Lighter indigo
    "primary_muted":    "#2D2F6B",   # Subdued indigo for backgrounds
    "accent":           "#A78BFA",   # Soft violet
    "accent_muted":     "#352B5E",   # Muted violet for tints

    # Text hierarchy
    "text":             "#F1F5F9",   # Primary text — near white
    "text_secondary":   "#CBD5E1",   # Secondary text
    "text_muted":       "#64748B",   # Tertiary / labels
    "text_tertiary":    "#475569",   # Disabled / faint

    # Borders & dividers
    "border":           "#1E293B",   # Subtle borders
    "border_light":     "#334155",   # Slightly visible borders
    "divider":          "#1E293B",   # Section dividers

    # Semantic colors — muted variants for backgrounds
    "success":          "#34D399",   # Emerald
    "success_muted":    "#0D3B2E",   # Emerald tint
    "danger":           "#F87171",   # Soft red
    "danger_muted":     "#3B1C1C",   # Red tint
    "warning":          "#FBBF24",   # Amber
    "warning_muted":    "#3B2F0F",   # Amber tint
    "info":             "#6366F1",   # Same as primary

    # Kanban column tints
    "kanban_discovery":   "#1A1E28",
    "kanban_qualified":   "#1A1F2E",
    "kanban_proposal":    "#1E1A2E",
    "kanban_meeting":     "#1A2E28",
    "kanban_negotiation": "#2E2A1A",
    "kanban_won":         "#1A2E1E",
    "kanban_lost":        "#2E1A1A",

    # Sidebar
    "sidebar_bg":       "#0D0F14",
    "sidebar_active":   "#1A1E28",
    "sidebar_accent":   "#6366F1",
    "sidebar_section":  "#475569",
}

# ─── TYPOGRAPHY ───────────────────────────────────────────────
# Segoe UI is guaranteed on Windows. Inter as conceptual fallback.
# Larger headings, thinner body, generous metric displays.
_FONT = "Segoe UI"

FONTS = {
    "display":    (_FONT, 32, "bold"),    # Hero numbers
    "heading1":   (_FONT, 24, "bold"),    # Page titles
    "heading2":   (_FONT, 16, "bold"),    # Section headers
    "heading3":   (_FONT, 14, "bold"),    # Card titles
    "metric":     (_FONT, 36, "bold"),    # Large dashboard numbers
    "body":       (_FONT, 13, "normal"),  # Body text
    "body_sm":    (_FONT, 12, "normal"),  # Small body text
    "small":      (_FONT, 11, "normal"),  # Small labels
    "caption":    (_FONT, 10, "bold"),    # Uppercase section labels
    "badge":      (_FONT, 10, "bold"),    # Badges / pills
    "nav":        (_FONT, 13, "normal"),  # Sidebar navigation
    "nav_section": (_FONT, 10, "bold"),   # Sidebar section headers
}

# ─── SPACING TOKENS ──────────────────────────────────────────
SPACING = {
    "3xs":  2,
    "xs":   4,
    "sm":   8,
    "md":   16,
    "lg":   24,
    "xl":   32,
    "2xl":  48,
    "3xl":  64,
}

# ─── RADIUS TOKENS ───────────────────────────────────────────
RADIUS = {
    "sm":   6,
    "md":   10,
    "lg":   14,
    "xl":   18,
    "full": 100,
}
