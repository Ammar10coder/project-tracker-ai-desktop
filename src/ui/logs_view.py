from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from core.workers import BackgroundWorker
from ui.dashboard_view import build_controller
from ui.widgets.page_header import PageHeader


class LogsView(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: BackgroundWorker | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        outer.addWidget(PageHeader(
            eyebrow="Live output",
            title="Logs",
            subtitle="Recent container output from the bot, pulled on demand.",
        ))

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 15, 18, 12)
        heading = QLabel("\u25A0  Activity log")
        heading.setObjectName("panelHeading")
        header_layout.addWidget(heading)
        header_layout.addStretch()

        self.meta = QLabel("Last checked \u2014")
        self.meta.setObjectName("logMeta")
        header_layout.addWidget(self.meta)

        self.btn_refresh = QPushButton("\u21BB")
        self.btn_refresh.setObjectName("ghostButton")
        self.btn_refresh.setFixedWidth(36)
        self.btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(self.btn_refresh)

        card_layout.addWidget(header)

        self.text = QPlainTextEdit()
        self.text.setObjectName("logBody")
        self.text.setReadOnly(True)
        self.text.setFrameShape(QFrame.NoFrame)
        card_layout.addWidget(self.text)

        outer.addWidget(card)

        self.refresh()

    def refresh(self):
        controller = build_controller()
        self.btn_refresh.setEnabled(False)

        self._worker = BackgroundWorker(controller.logs, 300)
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def _on_done(self, success: bool, result):
        self.btn_refresh.setEnabled(True)
        if not success:
            self.text.setPlainText(f"Error fetching logs: {result}")
            self.meta.setText("Couldn't load logs")
            return
        self.text.setPlainText(result.output or "No activity yet.")
        self.meta.setText("Last checked " + datetime.now().strftime("%I:%M:%S %p"))
