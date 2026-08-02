"""
Basic sanity test for AppSettings. Run with:  pytest tests/
Does not require a display / Qt to run.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app_config import AppSettings  # noqa: E402


def test_defaults_load_without_error():
    s = AppSettings.load()
    assert s.mode in ("local", "remote")
    assert isinstance(s.container_name, str)


def test_save_and_reload_roundtrip(tmp_path, monkeypatch):
    import app_config

    fake_file = tmp_path / "settings.json"
    monkeypatch.setattr(app_config, "SETTINGS_FILE", fake_file)

    s = AppSettings()
    s.local_project_dir = r"C:\test\project_tracker_ai"
    s.save()

    assert fake_file.exists()
