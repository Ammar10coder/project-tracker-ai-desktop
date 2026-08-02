from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app_config import settings
from core.db_reader import DBReader
from ui.widgets.page_header import PageHeader


class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        outer.addWidget(PageHeader(
            eyebrow="Daily summaries",
            title="Reports",
            subtitle="Browse generated daily_reports entries from the bot's database.",
        ))

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 15, 18, 15)

        header = QHBoxLayout()
        heading = QLabel("\u25A0  Daily reports")
        heading.setObjectName("panelHeading")
        header.addWidget(heading)
        header.addStretch()
        self.btn_refresh = QPushButton("\u21BB  Refresh")
        self.btn_refresh.setObjectName("ghostButton")
        self.btn_refresh.clicked.connect(self.refresh)
        header.addWidget(self.btn_refresh)
        card_layout.addLayout(header)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date", "Overall status", "Deadline risk"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.itemSelectionChanged.connect(self._show_selected)
        card_layout.addWidget(self.table)

        outer.addWidget(card, 1)

        summary_card = QFrame()
        summary_card.setObjectName("card")
        summary_layout = QVBoxLayout(summary_card)
        summary_heading = QLabel("Summary")
        summary_heading.setObjectName("panelHeading")
        summary_layout.addWidget(summary_heading)

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setFrameShape(QFrame.NoFrame)
        summary_layout.addWidget(self.summary_box)

        outer.addWidget(summary_card, 1)

        self._rows: list[tuple] = []
        self.refresh()

    def refresh(self):
        reader = DBReader(settings.db_path)
        self._rows = reader.recent_reports(limit=30)
        self.table.setRowCount(len(self._rows))
        for i, (date, status, risk, _summary) in enumerate(self._rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(date)))
            self.table.setItem(i, 1, QTableWidgetItem(str(status)))
            self.table.setItem(i, 2, QTableWidgetItem(str(risk)))

    def _show_selected(self):
        row = self.table.currentRow()
        if 0 <= row < len(self._rows):
            self.summary_box.setPlainText(self._rows[row][3] or "")
