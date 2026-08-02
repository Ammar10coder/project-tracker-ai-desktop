"""
app_config.py
=============
Single source of truth for configuration.

Load order (later wins):
  1. Bundled defaults
  2. ".env" next to the executable (git-ignored, created by the user
     from .env.example)
  3. "%APPDATA%\\ProjectTrackerAI\\settings.json" — written when the
     user edits settings from inside the Settings tab, so changes
     persist across restarts without touching the .env file.

This module never talks to the network and never writes secrets to
disk anywhere except the two files above, both of which live outside
the install/build folders and are never part of the Git repo.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from dotenv import load_dotenv


def _base_dir() -> Path:
    """Folder the .exe (or script) lives in — used to find a local .env."""
    if getattr(sys, "frozen", False):  # running as a PyInstaller .exe
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def _appdata_dir() -> Path:
    root = os.environ.get("APPDATA") or str(Path.home() / ".config")
    d = Path(root) / "ProjectTrackerAI"
    d.mkdir(parents=True, exist_ok=True)
    return d


SETTINGS_FILE = _appdata_dir() / "settings.json"

# Load .env (if present) before reading any os.environ values below.
load_dotenv(_base_dir() / ".env")


@dataclass
class AppSettings:
    mode: str = "local"  # "local" or "remote"

    local_project_dir: str = os.getenv("PTA_LOCAL_PROJECT_DIR", "")

    remote_host: str = os.getenv("PTA_REMOTE_HOST", "")
    remote_user: str = os.getenv("PTA_REMOTE_USER", "")
    remote_ssh_key_path: str = os.getenv("PTA_REMOTE_SSH_KEY_PATH", "")
    remote_project_dir: str = os.getenv("PTA_REMOTE_PROJECT_DIR", "")

    container_name: str = os.getenv("PTA_CONTAINER_NAME", "project_tracker_ai")
    db_path: str = os.getenv("PTA_DB_PATH", "")

    def __post_init__(self):
        self.mode = os.getenv("PTA_MODE", self.mode)

    @classmethod
    def load(cls) -> "AppSettings":
        settings = cls()
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                for key, value in data.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
            except (json.JSONDecodeError, OSError):
                pass  # fall back to .env / defaults silently
        return settings

    def save(self) -> None:
        SETTINGS_FILE.write_text(
            json.dumps(asdict(self), indent=2), encoding="utf-8"
        )


settings = AppSettings.load()
