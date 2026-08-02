from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

# Palette lifted directly from the reference design's CSS custom properties.
INK = QColor("#0F2018")
MUTED = QColor("#5C6F63")
PANEL = QColor("#FFFFFF")
BORDER = QColor(15, 32, 24, 31)  # rgba(15,32,24,0.12)
LIVE = QColor("#2CA85E")
STOPPED = QColor("#B8842A")
DANGER = QColor("#B23B2E")
NEUTRAL = QColor("#5C6F63")


class StatusCard(QWidget):
    """Reproduces the reference design's HUD-framed status pill:
    corner brackets, a status dot with a pulsing ring while running,
    a bold label, and a muted subtitle line underneath.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 64)
        self._label = "Checking..."
        self._sub = "Looking for the container"
        self._color = NEUTRAL
        self._pulse_radius = 6.0
        self._pulsing = False

        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._tick_pulse)

    def set_state(self, label: str, sub: str, color: QColor, pulsing: bool = False):
        self._label = label
        self._sub = sub
        self._color = color
        self._pulsing = pulsing
        if pulsing and not self._timer.isActive():
            self._pulse_radius = 6.0
            self._timer.start()
        elif not pulsing:
            self._timer.stop()
        self.update()

    def _tick_pulse(self):
        self._pulse_radius += 0.6
        if self._pulse_radius > 22:
            self._pulse_radius = 6.0
        self.update()

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(1, 1, -1, -1)

        # Card background
        painter.setPen(QPen(BORDER, 1))
        painter.setBrush(PANEL)
        painter.drawRoundedRect(rect, 14, 14)

        # HUD corner brackets (top-left, bottom-right), like a viewfinder
        bracket = 16
        pen = QPen(LIVE, 2)
        painter.setPen(pen)
        # top-left
        painter.drawLine(rect.left(), rect.top() + bracket, rect.left(), rect.top())
        painter.drawLine(rect.left(), rect.top(), rect.left() + bracket, rect.top())
        # bottom-right
        painter.drawLine(rect.right() - bracket, rect.bottom(), rect.right(), rect.bottom())
        painter.drawLine(rect.right(), rect.bottom(), rect.right(), rect.bottom() - bracket)

        # Pulsing ring behind the dot
        dot_cx, dot_cy, dot_r = 32, rect.height() / 2 + rect.top(), 6
        if self._pulsing:
            ring_alpha = max(0, int(140 * (1 - (self._pulse_radius - 6) / 16)))
            ring_color = QColor(self._color)
            ring_color.setAlpha(ring_alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(ring_color)
            painter.drawEllipse(
                QRectF(dot_cx - self._pulse_radius, dot_cy - self._pulse_radius,
                       self._pulse_radius * 2, self._pulse_radius * 2)
            )

        # Status dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._color)
        painter.drawEllipse(QRectF(dot_cx - dot_r, dot_cy - dot_r, dot_r * 2, dot_r * 2))

        # Text
        label_font = QFont("Segoe UI Semibold", 11)
        painter.setFont(label_font)
        painter.setPen(INK)
        text_x = dot_cx + 18
        painter.drawText(text_x, int(dot_cy - 2), self._label)

        sub_font = QFont("Segoe UI", 9)
        painter.setFont(sub_font)
        painter.setPen(MUTED)
        painter.drawText(text_x, int(dot_cy + 14), self._sub)

        painter.end()
