"""
utils/helpers.py
==================
Two things every packaged desktop app needs and a script never does:

1. resource_path() — bundled data files (icon, .qss) live inside a
   temp extraction folder (sys._MEIPASS) once PyInstaller has built a
   --onefile .exe. Plain relative paths like "assets/icon.ico" break
   the moment you run the compiled exe, even though they work fine
   with `python src/main.py`. This resolves correctly in both cases.

2. setup_crash_handler() — with console=False (no terminal window),
   an uncaught exception makes the app silently disappear with no
   clue why. This installs a global excepthook that writes the full
   traceback to %APPDATA%\\ProjectTrackerAI\\crash.log and shows the
   user a dialog instead of a silent vanish.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """Resolve a bundled resource path for both `python src/main.py`
    (dev) and the compiled .exe (frozen) cases.

    relative_path is always given relative to the project root, e.g.
    "assets/icon.ico" or "src/ui/theme.qss" — this must match how the
    files are declared in build/pyinstaller.spec's `datas` list.
    """
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # PyInstaller's extraction folder
    else:
        # src/utils/helpers.py -> project root is two levels up
        base = Path(__file__).resolve().parent.parent.parent
    return str(base / relative_path)


def setup_crash_handler(app_name: str = "ProjectTrackerAI") -> Path:
    """Install a global excepthook. Returns the crash log path.

    Must be called AFTER a QApplication instance exists, otherwise the
    QMessageBox shown on crash has no event loop to attach to.
    """
    app_data = Path(os.getenv("APPDATA", str(Path.home()))) / app_name
    app_data.mkdir(parents=True, exist_ok=True)
    log_file = app_data / "crash.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    def log_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Unhandled Exception:", exc_info=(exc_type, exc_value, exc_traceback))

        try:
            # Imported lazily so this module has no hard PySide6
            # dependency for non-GUI uses (e.g. CI/tests).
            from PySide6.QtWidgets import QMessageBox

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Application Error")
            msg.setText("An unexpected error occurred and the app needs to close this dialog to continue.")
            msg.setInformativeText(f"{exc_value}\n\nFull details saved to:\n{log_file}")
            msg.exec()
        except Exception:
            # If even the error dialog can't show, at least the log file has it.
            pass

    sys.excepthook = log_exception
    return log_file
