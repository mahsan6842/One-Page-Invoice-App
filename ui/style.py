"""
UI style tokens and ttk theme configuration.
"""

from tkinter import ttk

# Color tokens
BASE_BG = "#F7F7F7"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#1F2937"
TEXT_MUTED = "#6B7280"
ACCENT = "#2563EB"
ACCENT_DARK = "#1D4ED8"
BORDER = "#E5E7EB"

# Typography
FONT_BASE = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_SMALL = ("Segoe UI", 9)

# Spacing (px)
PADDING_XS = 4
PADDING_S = 6
PADDING_M = 10
PADDING_L = 16


def setup_styles(style: ttk.Style) -> None:
    """Configure ttk styles for a modern light UI."""
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Base styles
    style.configure(".", font=FONT_BASE)
    style.configure("TLabel", foreground=TEXT_PRIMARY)
    style.configure("App.TFrame", background=BASE_BG)
    style.configure("AppCard.TFrame", background=CARD_BG)

    # Typography helpers
    style.configure("Header.TLabel", font=FONT_HEADER, foreground=TEXT_PRIMARY)
    style.configure("Muted.TLabel", font=FONT_SMALL, foreground=TEXT_MUTED)

    # Buttons
    style.configure("TButton", padding=(10, 6))
    style.configure("Toolbar.TButton", padding=(10, 4))
    style.map("TButton", foreground=[("disabled", TEXT_MUTED)])

    style.configure("Primary.TButton", background=ACCENT, foreground="white", padding=(12, 6))
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_DARK), ("disabled", BORDER)],
        foreground=[("active", "white"), ("disabled", TEXT_MUTED)],
    )

    # Treeview
    style.configure("App.Treeview", rowheight=28)
    style.configure("App.Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # Status bar
    style.configure("Status.TLabel", font=FONT_SMALL, foreground=TEXT_MUTED)

    # Form sections
    style.configure("Section.TLabelframe", padding=12)
    style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground=TEXT_PRIMARY)
