from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app_config import settings
from ui.widgets.page_header import PageHeader


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        outer.addWidget(PageHeader(
            eyebrow="Configuration",
            title="Settings",
            subtitle="Connection details only \u2014 secrets always stay in your local .env file.",
        ))

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        # ---- Mode selector, always visible -------------------------------
        mode_form = QFormLayout()
        mode_form.setSpacing(10)
        self.mode = QComboBox()
        self.mode.addItems(["local", "remote"])
        self.mode.setCurrentText(settings.mode)
        self.mode.currentTextChanged.connect(self._on_mode_changed)
        mode_form.addRow("Mode", self.mode)
        card_layout.addLayout(mode_form)

        # ---- Local-only group ----------------------------------------------
        self.local_group = QWidget()
        local_form = QFormLayout(self.local_group)
        local_form.setContentsMargins(0, 0, 0, 0)
        local_form.setSpacing(10)
        local_hint = QLabel("Used when Mode = local (Docker Desktop on this PC).")
        local_hint.setObjectName("hintText")
        local_form.addRow(local_hint)
        self.local_dir = QLineEdit(settings.local_project_dir)
        local_form.addRow("Local project folder", self.local_dir)
        card_layout.addWidget(self.local_group)

        # ---- Remote-only group ------------------------------------------
        self.remote_group = QWidget()
        remote_form = QFormLayout(self.remote_group)
        remote_form.setContentsMargins(0, 0, 0, 0)
        remote_form.setSpacing(10)
        remote_hint = QLabel("Used when Mode = remote (Oracle Cloud over SSH). Docker Desktop is not needed on this PC.")
        remote_hint.setObjectName("hintText")
        remote_hint.setWordWrap(True)
        remote_form.addRow(remote_hint)
        self.remote_host = QLineEdit(settings.remote_host)
        remote_form.addRow("Remote host (Oracle Cloud IP)", self.remote_host)
        self.remote_user = QLineEdit(settings.remote_user)
        remote_form.addRow("Remote user", self.remote_user)
        self.remote_key = QLineEdit(settings.remote_ssh_key_path)
        remote_form.addRow("SSH private key path", self.remote_key)
        self.remote_dir = QLineEdit(settings.remote_project_dir)
        remote_form.addRow("Remote project folder", self.remote_dir)
        card_layout.addWidget(self.remote_group)

        # ---- Shared fields, always visible ---------------------------------
        shared_form = QFormLayout()
        shared_form.setSpacing(10)
        self.container_name = QLineEdit(settings.container_name)
        shared_form.addRow("Docker container name", self.container_name)
        self.db_path = QLineEdit(settings.db_path)
        shared_form.addRow("SQLite DB path (read-only)", self.db_path)
        card_layout.addLayout(shared_form)

        note = QLabel(
            "Credentials such as API keys stay in your local .env file and are "
            "never shown or edited here. This screen only stores connection "
            "settings, saved to %APPDATA%\\ProjectTrackerAI\\settings.json."
        )
        note.setObjectName("heroSub")
        note.setWordWrap(True)
        card_layout.addWidget(note)

        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self.save)
        card_layout.addWidget(save_btn)

        outer.addWidget(card)
        outer.addStretch()

        self._on_mode_changed(self.mode.currentText())

    def _on_mode_changed(self, mode: str):
        self.local_group.setVisible(mode == "local")
        self.remote_group.setVisible(mode == "remote")

    def save(self):
        settings.mode = self.mode.currentText()
        settings.local_project_dir = self.local_dir.text().strip()
        settings.remote_host = self.remote_host.text().strip()
        settings.remote_user = self.remote_user.text().strip()
        settings.remote_ssh_key_path = self.remote_key.text().strip()
        settings.remote_project_dir = self.remote_dir.text().strip()
        settings.container_name = self.container_name.text().strip()
        settings.db_path = self.db_path.text().strip()
        settings.save()
        QMessageBox.information(self, "Saved", "Settings saved. Restart not required.")
