"""
ssh_controller.py
==================
Mirrors DockerController's interface but runs the same docker/docker-compose
commands on a remote host (e.g. the Oracle Cloud Always-Free VM) over SSH,
using a private key — never a password.

Used when AppSettings.mode == "remote".
"""
from __future__ import annotations

from dataclasses import dataclass

import paramiko

from core.docker_controller import CommandResult


class SSHController:
    def __init__(self, host: str, user: str, key_path: str, project_dir: str, container_name: str):
        self.host = host
        self.user = user
        self.key_path = key_path
        self.project_dir = project_dir
        self.container_name = container_name

    def _exec(self, remote_cmd: str, timeout: int = 120) -> CommandResult:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=self.host,
                username=self.user,
                key_filename=self.key_path,
                timeout=15,
            )
            _stdin, stdout, stderr = client.exec_command(remote_cmd, timeout=timeout)
            out = stdout.read().decode(errors="replace")
            err = stderr.read().decode(errors="replace")
            exit_code = stdout.channel.recv_exit_status()
            return CommandResult(ok=exit_code == 0, output=(out + err).strip())
        except Exception as exc:  # noqa: BLE001 - surfaced directly in the UI
            return CommandResult(False, f"SSH error: {exc}")
        finally:
            client.close()

    def _compose(self) -> str:
        # Prefer the v2 plugin form; fall back to legacy docker-compose.
        return (
            f"cd {self.project_dir} && "
            f"(docker compose version >/dev/null 2>&1 && docker compose"
            f" || docker-compose)"
        )

    def status(self) -> CommandResult:
        return self._exec(
            f"docker inspect -f '{{{{.State.Status}}}}' {self.container_name}"
        )

    def start(self) -> CommandResult:
        return self._exec(f"{self._compose()} up -d")

    def stop(self) -> CommandResult:
        return self._exec(f"{self._compose()} down")

    def restart(self) -> CommandResult:
        stopped = self.stop()
        if not stopped.ok:
            return stopped
        return self.start()

    def logs(self, lines: int = 200) -> CommandResult:
        return self._exec(f"docker logs --tail {lines} {self.container_name}")

    def rebuild(self) -> CommandResult:
        cmd = f"{self._compose()} down && {self._compose()} build --no-cache && {self._compose()} up -d"
        return self._exec(cmd, timeout=600)
