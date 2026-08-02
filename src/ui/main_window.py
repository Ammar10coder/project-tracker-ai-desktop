from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from ui.dashboard_view import DashboardView
from ui.logs_view import LogsView
from ui.reports_view import ReportsView
from ui.settings_view import SettingsView
from ui.widgets.blueprint_background import BlueprintBackground
from utils.helpers import resource_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Tracker AI — Control Panel")
        self.resize(920, 680)

        icon_path = resource_path("assets/icon.ico")
        if Path(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))

        root = BlueprintBackground()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_titlebar())

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(DashboardView(), "Dashboard")
        tabs.addTab(LogsView(), "Logs")
        tabs.addTab(ReportsView(), "Reports")
        tabs.addTab(SettingsView(), "Settings")
        root_layout.addWidget(tabs, 1)

        footer = QLabel("Kelvin6k \u00b7 Robotic & Sustainable Construction Technology")
        footer.setObjectName("windowFooter")
        footer.setAlignment(Qt.AlignCenter)
        footer.setContentsMargins(0, 6, 0, 10)
        root_layout.addWidget(footer)

        self.setCentralWidget(root)

    def _build_titlebar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("titlebar")
        bar.setFixedHeight(46)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(10)

        logo_path = resource_path("assets/logo.jpg")
        if Path(logo_path).exists():
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(22, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            layout.addWidget(logo_label)

        brand = QLabel("AUTOMATION DESK")
        brand.setObjectName("brandLabel")
        layout.addWidget(brand)

        layout.addStretch()
        return bar
