"""
docker_controller.py
=====================
Runs docker / docker-compose commands against a LOCAL Docker Desktop
installation. Used when AppSettings.mode == "local".

All calls run in a worker thread from the UI layer (see ui/dashboard_view.py)
so the GUI never freezes while waiting on Docker.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

# Prevents a black console window from flashing open on Windows
# every time we shell out to docker.exe.
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


@dataclass
class CommandResult:
    ok: bool
    output: str


class DockerController:
    def __init__(self, project_dir: str, container_name: str):
        self.project_dir = project_dir
        self.container_name = container_name

    def _run(self, args: list[str], cwd: str | None = None, timeout: int = 120) -> CommandResult:
        try:
            result = subprocess.run(
                args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=_CREATE_NO_WINDOW,
            )
            ok = result.returncode == 0
            out = (result.stdout or "") + (result.stderr or "")
            return CommandResult(ok=ok, output=out.strip())
        except FileNotFoundError:
            return CommandResult(ok=False, output=f"Command not found: {args[0]}. Is Docker Desktop installed and on PATH?")
        except subprocess.TimeoutExpired:
            return CommandResult(ok=False, output="Command timed out.")

    def _compose_prefix(self) -> list[str]:
        probe = self._run(["docker-compose", "version"])
        return ["docker-compose"] if probe.ok else ["docker", "compose"]

    def status(self) -> CommandResult:
        return self._run(
            ["docker", "inspect", "-f", "{{.State.Status}}", self.container_name],
            timeout=15,
        )

    def start(self) -> CommandResult:
        if not os.path.isdir(self.project_dir):
            return CommandResult(False, f"Project folder not found: {self.project_dir}")
        cmd = self._compose_prefix() + ["up", "-d"]
        return self._run(cmd, cwd=self.project_dir, timeout=180)

    def stop(self) -> CommandResult:
        if not os.path.isdir(self.project_dir):
            return CommandResult(False, f"Project folder not found: {self.project_dir}")
        cmd = self._compose_prefix() + ["down"]
        return self._run(cmd, cwd=self.project_dir, timeout=120)

    def restart(self) -> CommandResult:
        stopped = self.stop()
        if not stopped.ok:
            return stopped
        return self.start()

    def logs(self, lines: int = 200) -> CommandResult:
        return self._run(
            ["docker", "logs", "--tail", str(lines), self.container_name],
            timeout=30,
        )

    def rebuild(self) -> CommandResult:
        """docker-compose down -> build --no-cache -> up -d (the correct
        redeploy sequence — restarting the container alone does NOT pick
        up code changes)."""
        if not os.path.isdir(self.project_dir):
            return CommandResult(False, f"Project folder not found: {self.project_dir}")
        prefix = self._compose_prefix()
        for step in (["down"], ["build", "--no-cache"], ["up", "-d"]):
            res = self._run(prefix + step, cwd=self.project_dir, timeout=600)
            if not res.ok:
                return res
        return CommandResult(True, "Rebuilt and started successfully.")
