"""
core/workers.py
=================
Every SSH connection, docker-compose call, or SQLite query MUST run off
the Qt GUI thread — otherwise the window freezes and Windows marks it
"Not Responding" during anything slower than a few milliseconds.

BackgroundWorker is a small QThread subclass used by every view
(dashboard, logs, reports) instead of hand-rolling QThread/moveToThread
boilerplate in each file.

Usage:
    self._worker = BackgroundWorker(controller.status)
    self._worker.finished.connect(self._on_done)
    self._worker.start()

    def _on_done(self, success: bool, result):
        # success=False, result=<error string> if target_func raised
        # success=True,  result=<whatever target_func returned> otherwise
        ...

Keep a reference to the worker on `self` (as above) for as long as it
might be running — otherwise Python can garbage-collect it mid-flight.
"""
from __future__ import annotations

from PySide6.QtCore import QThread, Signal


class BackgroundWorker(QThread):
    """Runs target_func(*args, **kwargs) on a background thread."""

    finished = Signal(bool, object)  # (success, result_or_error_message)

    def __init__(self, target_func, *args, **kwargs):
        super().__init__()
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.target_func(*self.args, **self.kwargs)
            self.finished.emit(True, result)
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI, not swallowed
            self.finished.emit(False, str(exc))
