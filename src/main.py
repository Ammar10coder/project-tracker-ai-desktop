"""
main.py
========
Entry point for the Project Tracker AI desktop control panel.

This launches a single native Qt window (PySide6/Qt Widgets). There is
no embedded web server, no localhost port, and no browser involved —
the compiled .exe is a self-contained GUI process.

Production hardening applied here:
  - resource_path()      -> assets/theme load correctly inside a
                             PyInstaller --onefile .exe (sys._MEIPASS)
  - setup_crash_handler() -> uncaught exceptions write to
                             %APPDATA%\\ProjectTrackerAI\\crash.log and
                             show a dialog instead of silently vanishing
  - AppUserModelID        -> Windows taskbar groups/pins this under its
                             own icon instead of a generic Python icon
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `import app_config`, `import core...`, `import ui...`, `import
# utils...` whether run as a script (python src/main.py) or frozen by
# PyInstaller (Analysis(pathex=[SRC]) bundles these the same way).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtGui import QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from ui.main_window import MainWindow  # noqa: E402
from utils.helpers import resource_path, setup_crash_handler  # noqa: E402


def _register_windows_taskbar_id() -> None:
    """No-op on non-Windows; on Windows, prevents the exe from being
    grouped under the generic Python icon in the taskbar."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        app_id = "ammar.projecttrackerai.desktop.1_0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass  # cosmetic only — never block startup over this


def main() -> int:
    _register_windows_taskbar_id()

    app = QApplication(sys.argv)
    app.setApplicationName("Project Tracker AI")
    app.setOrganizationName("Ammar")

    # Crash handler needs a live QApplication to show its dialog, so it
    # is installed right after QApplication() rather than before.
    setup_crash_handler("ProjectTrackerAI")

    icon_path = resource_path("assets/icon.ico")
    if Path(icon_path).exists():
        app.setWindowIcon(QIcon(icon_path))

    qss_path = resource_path("src/ui/theme.qss")
    if Path(qss_path).exists():
        app.setStyleSheet(Path(qss_path).read_text(encoding="utf-8"))

    window = MainWindow()
    if Path(icon_path).exists():
        window.setWindowIcon(QIcon(icon_path))
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
