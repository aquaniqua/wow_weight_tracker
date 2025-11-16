import tkinter as tk
from tkinter import ttk

def setup_theme():
    """Configure ttk theme with purple WoW-style colors."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Purple.Horizontal.TProgressbar",
        troughcolor="#281b38",
        background="#6b59b3",
        darkcolor="#5c4aa4",
        lightcolor="#7a68c4",
        bordercolor="#1d1230",
    )
    return style

