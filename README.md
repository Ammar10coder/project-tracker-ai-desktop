# Project Tracker AI — Desktop Control Panel (Windows)

A native Windows desktop app (PySide6/Qt) that starts, stops, monitors, and
reports on the existing `project_tracker_ai` Telegram bot — whether it runs
locally in Docker or remotely on your Oracle Cloud VM.

**This is a real desktop GUI, not a browser wrapper.** There is no
localhost web server, no Flask/Streamlit process, and no page opened in a
browser. `main.py` opens a single native Qt window; compiled with
PyInstaller it becomes one `.exe` that runs standalone.

> Note: the earlier macOS build (`Project Tracker AI.app`) launched a local
> HTTP server (`server.py`) and rendered `web/index.html` — that pattern is
> intentionally **not** reused here, per the "no localhost web app" requirement.

---

## 1. Project structure

```
ProjectTrackerAI-Desktop/
├── .github/workflows/
│   └── build-windows.yml      # CI: builds + tests the exe on every push
├── assets/
│   └── icon.ico                # app icon, embedded into the exe
├── build/
│   ├── pyinstaller.spec        # PyInstaller build spec (--onefile, no console)
│   └── installer.iss           # Inno Setup script -> ProjectTrackerAI-Setup.exe
├── src/
│   ├── main.py                  # entry point — opens the native Qt window
│   ├── app_config.py            # loads .env + persists settings.json
│   ├── core/
│   │   ├── docker_controller.py # local docker-compose control (subprocess)
│   │   ├── ssh_controller.py    # remote (Oracle Cloud) control over SSH
│   │   └── db_reader.py         # read-only SQLite access for dashboard stats
│   └── ui/
│       ├── main_window.py       # QMainWindow with tabs
│       ├── dashboard_view.py    # status, start/stop/rebuild, task summary
│       ├── logs_view.py         # live container logs
│       ├── reports_view.py      # browse daily_reports table
│       ├── settings_view.py     # edit connection settings (no secrets)
│       └── theme.qss            # Qt stylesheet
├── tests/
│   └── test_settings_store.py
├── .env.example                 # placeholder config — copy to .env
├── .gitignore                   # keeps secrets & build output out of Git
├── requirements.txt              # runtime dependencies
├── requirements-build.txt        # runtime + PyInstaller
├── build_windows.bat              # one-click build script
└── README.md
```

This folder is meant to sit as its own GitHub repo (or a `desktop-app/`
subfolder inside your existing `project_tracker_ai` repo) — it doesn't
duplicate the bot's backend code, it controls it.

---

## 2. How it talks to the bot

Two modes, switchable in the **Settings** tab (stored in
`%APPDATA%\ProjectTrackerAI\settings.json`, never in Git):

| Mode | Use case | How it works |
|---|---|---|
| `local` | Docker Desktop running on the same Windows PC | shells out to `docker` / `docker-compose` via `subprocess` |
| `remote` | Bot deployed on your Oracle Cloud Always-Free VM | connects over SSH (`paramiko`) using a private key, runs the same docker commands remotely |

Dashboard/report stats are read directly from the bot's SQLite database
(`project.db`) in **read-only** mode (`sqlite3` opened with `mode=ro`), so
the desktop app can never corrupt data the bot container is writing.

---

## 3. Security: API keys & credentials

- All secrets (Telegram API ID/hash, Gemini/Groq keys, Gmail app password,
  SSH key **path**) are read from a local `.env` file — never hardcoded.
- `.env` is listed in `.gitignore` and is **never** committed.
- `.env.example` ships in the repo with placeholder values only, so a new
  clone can be configured with `copy .env.example .env` + fill in values.
- The Settings tab only edits *connection* details (host, folder paths,
  container name) — actual secrets stay in `.env` and are not displayed
  or editable in the UI.
- The SSH controller connects with a private key file, never a password.
- The installer (Inno Setup) does not require admin rights and installs
  to the current user's local app folder.

**Before pushing this repo to GitHub**, double-check no real `.env`,
`*.session`, `client_secrets.json`, or `mycreds.txt` files are staged —
the provided `.gitignore` already excludes them, but always run
`git status` and confirm the diff before your first commit if you're
folding in files from an existing local project.

---

## 4. Build instructions (produces the standalone `.exe`)

Run these **on a Windows machine** (Python builds are platform-specific;
a Windows `.exe` cannot be produced by building on macOS/Linux).

### Prerequisites
- Windows 10/11
- [Python 3.11+](https://www.python.org/downloads/) (check "Add to PATH" during install)
- Docker Desktop (only needed at *runtime* if you use local mode)
- Optional, for the installer: [Inno Setup 6](https://jrsoftware.org/isdl.php)

### Step 1 — Get the code
```powershell
git clone https://github.com/<your-username>/project-tracker-ai-desktop.git
cd project-tracker-ai-desktop
```

### Step 2 — Configure secrets
```powershell
copy .env.example .env
notepad .env
```
Fill in your project folder path / remote host details. Real API keys for
the bot itself live in the **bot's own** `.env` (on the Oracle Cloud VM or
your local `project_tracker_ai` folder) — this app's `.env` only needs
connection info, not the bot's Gemini/Telegram keys, unless you enable the
optional AI summary feature.

### Step 3 — One-click build
```powershell
build_windows.bat
```
This script:
1. Creates a `.venv` virtual environment
2. Installs dependencies from `requirements-build.txt`
3. Runs PyInstaller with `build\pyinstaller.spec`
4. Outputs **`dist\ProjectTrackerAI.exe`** — a single, standalone,
   double-clickable Windows application (no console window, no installer
   required to run it).

### Step 4 (optional) — Build a proper installer
Produces `ProjectTrackerAI-Setup.exe` with Start Menu + Desktop shortcuts:
```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss
```
Output: `build\Output\ProjectTrackerAI-Setup.exe`

### Manual build (equivalent to the .bat, step by step)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-build.txt
pyinstaller build\pyinstaller.spec --distpath dist --workpath build\work --noconfirm
```

---

## 5. Running from source (no build)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\main.py
```

---

## 6. GitHub repo checklist

- [x] `.gitignore` excludes `.env`, sessions, DB files, and build output
- [x] `.env.example` with placeholders only
- [x] `requirements.txt` pinned versions
- [x] CI workflow (`.github/workflows/build-windows.yml`) builds + tests
      the exe on every push, so a broken build is caught before release
- [ ] Add a `LICENSE` file of your choice
- [ ] Tag releases (e.g. `v1.0.0`) and attach `ProjectTrackerAI-Setup.exe`
      as a GitHub Release asset once built
