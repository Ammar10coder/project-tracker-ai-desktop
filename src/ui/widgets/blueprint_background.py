from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

GRID_STEP = 28
GRID_COLOR = QColor(27, 42, 102, 14)  # steel navy at low alpha, matching the reference site-drawing grid


class BlueprintBackground(QWidget):
    """A faint grid background, like a site drawing / blueprint sheet.

    Used behind the main content area to echo the reference web design's
    `linear-gradient` grid pattern, since Qt stylesheets don't support
    generated tiled gradients the way CSS does.
    """

    def paintEvent(self, event):  # noqa: N802 - Qt naming convention
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        pen = QPen(GRID_COLOR)
        pen.setWidth(1)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        for x in range(0, w, GRID_STEP):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, GRID_STEP):
            painter.drawLine(0, y, w, y)
        painter.end()
