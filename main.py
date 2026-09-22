from __future__ import annotations

import ctypes
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from app.deck import CardDataError, load_deck
from app.ui import TarotApp


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def enable_windows_dpi_awareness() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError, OSError, ValueError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError, ValueError):
            pass


def main() -> int:
    enable_windows_dpi_awareness()
    root = tk.Tk()
    root.withdraw()
    try:
        cards = load_deck(resource_path("data"))
    except CardDataError as exc:
        messagebox.showerror("Signal Tarot — Deck Error", str(exc), parent=root)
        root.destroy()
        return 1

    TarotApp(
        root,
        cards,
        resource_path("packaging/speak.ps1"),
        resource_path("assets/deck/thumbnails"),
    )
    root.deiconify()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
