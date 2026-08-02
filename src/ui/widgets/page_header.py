from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PageHeader(QWidget):
    """Small eyebrow + title (+ optional subtitle), reused at the top of
    every tab so Dashboard/Logs/Reports/Settings read as one continuous
    app instead of four separately-styled screens.

    Dashboard uses the larger `heroTitle` size (it's the "home" tab);
    the other tabs use the slightly smaller `pageTitle` size.
    """

    def __init__(self, eyebrow: str, title: str, subtitle: str = "", large: bool = False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        eyebrow_label = QLabel(eyebrow.upper())
        eyebrow_label.setObjectName("eyebrow")
        layout.addWidget(eyebrow_label)

        title_label = QLabel(title)
        title_label.setObjectName("heroTitle" if large else "pageTitle")
        layout.addWidget(title_label)

        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setObjectName("heroSub")
            layout.addWidget(sub_label)
