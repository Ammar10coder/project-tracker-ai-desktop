# PyInstaller spec — produces ONE standalone .exe (no console window,
# no browser, no localhost server). Build from the project root with:
#     pyinstaller build/pyinstaller.spec
#
# SPECPATH (provided automatically by PyInstaller) is the folder this
# .spec file lives in (build/), so paths are resolved from there —
# this makes the build work regardless of which directory you run the
# `pyinstaller` command from.

# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH).resolve().parent  # project root
SRC = ROOT / "src"

a = Analysis(
    [str(SRC / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        # Destination paths here MUST match the relative_path strings
        # passed to resource_path() in src/utils/helpers.py.
        (str(ROOT / "assets"), "assets"),
        (str(SRC / "ui" / "theme.qss"), "src/ui"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "paramiko",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# NOTE: no COLLECT() step — passing a.binaries/a.zipfiles/a.datas
# straight into EXE() below is what makes this a single-file
# (--onefile-equivalent) build. Do not add onefile=... to EXE(); that
# is not a real PyInstaller argument and will raise a TypeError.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ProjectTrackerAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no console window: real desktop app
    disable_windowed_traceback=False,
    icon=str(ROOT / "assets" / "icon.ico"),
)
