from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app_config import settings
from core.db_reader import DBReader
from core.docker_controller import CommandResult, DockerController
from core.ssh_controller import SSHController
from core.workers import BackgroundWorker
from ui.widgets.page_header import PageHeader
from ui.widgets.status_card import DANGER, LIVE, STOPPED, StatusCard


def build_controller():
    if settings.mode == "remote":
        return SSHController(
            host=settings.remote_host,
            user=settings.remote_user,
            key_path=settings.remote_ssh_key_path,
            project_dir=settings.remote_project_dir,
            container_name=settings.container_name,
        )
    return DockerController(
        project_dir=settings.local_project_dir,
        container_name=settings.container_name,
    )


class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: BackgroundWorker | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        # ---------------- Hero: page header + status card -----------------
        hero = QHBoxLayout()
        hero.setSpacing(20)

        header = PageHeader(
            eyebrow="Project progress tracker",
            title="Control Panel",
            subtitle="Start it, stop it, and see what it's doing.",
            large=True,
        )
        hero.addWidget(header, 1)

        self.status_card = StatusCard()
        hero.addWidget(self.status_card, 0, Qt.AlignTop)

        outer.addLayout(hero)

        # ---------------- Mode badge ----------------------------------------
        mode_row = QHBoxLayout()
        self.mode_badge = QLabel()
        mode_row.addWidget(self.mode_badge)
        self.mode_hint = QLabel()
        self.mode_hint.setObjectName("hintText")
        mode_row.addWidget(self.mode_hint)
        mode_row.addStretch()
        outer.addLayout(mode_row)
        self._update_mode_badge()

        # ---------------- Controls row ------------------------------------
        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.btn_start = QPushButton("\u25B6  Start bot")
        self.btn_stop = QPushButton("\u25A0  Stop bot")
        self.btn_stop.setObjectName("dangerButton")
        self.btn_refresh = QPushButton("\u21BB  Refresh")
        self.btn_refresh.setObjectName("ghostButton")
        self.btn_rebuild = QPushButton("Rebuild (code changes)")
        self.btn_rebuild.setObjectName("ghostButton")
        for b, slot in (
            (self.btn_start, lambda: self._run_action("start")),
            (self.btn_stop, lambda: self._run_action("stop")),
            (self.btn_refresh, self.refresh_status),
            (self.btn_rebuild, self._confirm_rebuild),
        ):
            b.clicked.connect(slot)
            controls.addWidget(b)
        controls.addStretch()
        outer.addLayout(controls)

        # ---------------- Feedback line ------------------------------------
        self.feedback = QLabel("")
        self.feedback.setObjectName("feedbackNeutral")
        outer.addWidget(self.feedback)

        # ---------------- Task summary card --------------------------------
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 15, 18, 15)

        heading_row = QHBoxLayout()
        heading = QLabel("\u25A0  Task summary by team member")
        heading.setObjectName("panelHeading")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        card_layout.addLayout(heading_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Total tasks", "Completed", "In progress", "Avg progress %"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFrameShape(QFrame.NoFrame)
        card_layout.addWidget(self.table)

        outer.addWidget(card, 1)

        self.refresh_status()
        self.refresh_stats()

    # ------------------------------------------------------------------
    def _update_mode_badge(self):
        if settings.mode == "remote":
            self.mode_badge.setText(f"REMOTE \u00b7 {settings.remote_host or 'no host set'}")
            self.mode_badge.setObjectName("modeBadgeRemote")
            self.mode_hint.setText("Controlling the bot over SSH \u2014 Docker Desktop is not required on this PC.")
        else:
            self.mode_badge.setText("LOCAL")
            self.mode_badge.setObjectName("modeBadgeLocal")
            self.mode_hint.setText("Controlling a local docker-compose project. Switch to Remote in Settings for Oracle Cloud.")
        self.mode_badge.style().unpolish(self.mode_badge)
        self.mode_badge.style().polish(self.mode_badge)

    def _set_feedback(self, text: str, kind: str = "neutral"):
        self.feedback.setText(text)
        self.feedback.setObjectName(
            {"ok": "feedbackOk", "err": "feedbackErr"}.get(kind, "feedbackNeutral")
        )
        self.feedback.style().unpolish(self.feedback)
        self.feedback.style().polish(self.feedback)

    def refresh_status(self):
        self._update_mode_badge()
        controller = build_controller()
        self.status_card.set_state("Checking...", "Looking for the container", STOPPED, pulsing=False)

        self._worker = BackgroundWorker(controller.status)
        self._worker.finished.connect(self._on_status_done)
        self._worker.start()

    def _on_status_done(self, success: bool, result):
        if not success:
            self.status_card.set_state("Can't reach the bot", str(result)[:60], DANGER, pulsing=False)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            return
        result: CommandResult = result
        state = result.output.strip().lower()
        if not result.ok:
            self.status_card.set_state("Not started yet", "Click Start bot to launch it", STOPPED, pulsing=False)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
        elif state == "running":
            self.status_card.set_state("Running", "Listening for updates in the group", LIVE, pulsing=True)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            self.status_card.set_state("Stopped", f"Container state: {state or 'unknown'}", STOPPED, pulsing=False)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def _run_action(self, action: str):
        controller = build_controller()
        fn = getattr(controller, action)
        for b in (self.btn_start, self.btn_stop, self.btn_rebuild):
            b.setEnabled(False)
        verb = {"start": "Starting", "stop": "Stopping", "rebuild": "Rebuilding"}.get(action, "Running")
        self._set_feedback(f"{verb} the bot... this can take a few seconds.", "neutral")

        self._worker = BackgroundWorker(fn)
        self._worker.finished.connect(lambda ok, res: self._on_action_done(action, ok, res))
        self._worker.start()

    def _on_action_done(self, action: str, success: bool, result):
        for b in (self.btn_start, self.btn_stop, self.btn_rebuild):
            b.setEnabled(True)
        if not success:
            self._set_feedback(self._friendly_error(str(result)), "err")
        else:
            result: CommandResult = result
            if result.ok:
                self._set_feedback(f"{action.capitalize()} succeeded.", "ok")
            else:
                self._set_feedback(self._friendly_error(result.output), "err")
        self.refresh_status()

    def _friendly_error(self, message: str) -> str:
        """Local-mode Docker errors get a nudge toward Remote mode instead
        of a raw 'docker.exe not found' dump, since that error is only
        relevant if you actually intend to run Docker on this PC."""
        if settings.mode == "local" and "docker" in message.lower() and (
            "not found" in message.lower() or "not recognized" in message.lower()
        ):
            return (
                "Docker Desktop isn't installed/on PATH on this PC. "
                "If the bot actually runs on Oracle Cloud, switch to Remote "
                "mode in Settings instead. Original error: " + message[-200:]
            )
        return message[-300:]

    def _confirm_rebuild(self):
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Rebuild container?",
            "This runs: down -> build --no-cache -> up -d.\n"
            "Use this after pushing code changes (a plain restart will NOT "
            "pick them up). Continue?",
        )
        if reply == QMessageBox.Yes:
            self._run_action("rebuild")

    def refresh_stats(self):
        reader = DBReader(settings.db_path)
        summaries = reader.employee_summaries()
        self.table.setRowCount(len(summaries))
        for row, s in enumerate(summaries):
            values = [s.name, str(s.total_tasks), str(s.completed), str(s.in_progress), f"{s.avg_progress:.0f}"]
            for col, val in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(val))
