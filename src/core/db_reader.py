"""
db_reader.py
=============
Read-only access to the project_tracker_ai SQLite database for dashboard
stats. Matches the schema in project_tracker_ai/app/models.py:

    tasks(id, task_name, status, progress, sender_name, chat_name, updated_at)
    daily_reports(id, report_date, summary, overall_status, deadline_risk)
    task_history(id, task_name, status, progress, sender_name, snapshot_date)

Opened in read-only mode (mode=ro) so the desktop app can never corrupt
the bot's live database, even if it's pointed at the same file the bot
container is writing to.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


@dataclass
class EmployeeSummary:
    name: str
    total_tasks: int
    completed: int
    in_progress: int
    avg_progress: float


class DBReader:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection | None:
        p = Path(self.db_path)
        if not p.is_file():
            return None
        uri = f"file:{quote(str(p))}?mode=ro"
        return sqlite3.connect(uri, uri=True, timeout=5)

    def is_reachable(self) -> bool:
        conn = self._connect()
        if conn is None:
            return False
        conn.close()
        return True

    def task_counts_by_status(self) -> dict[str, int]:
        conn = self._connect()
        if conn is None:
            return {}
        try:
            cur = conn.execute(
                "SELECT COALESCE(status, 'Unknown'), COUNT(*) FROM tasks GROUP BY status"
            )
            return dict(cur.fetchall())
        finally:
            conn.close()

    def employee_summaries(self) -> list[EmployeeSummary]:
        conn = self._connect()
        if conn is None:
            return []
        try:
            cur = conn.execute(
                """
                SELECT
                    COALESCE(sender_name, 'Unknown') AS name,
                    COUNT(*) AS total,
                    SUM(CASE WHEN LOWER(status) LIKE '%complete%' THEN 1 ELSE 0 END) AS done,
                    SUM(CASE WHEN LOWER(status) LIKE '%progress%' THEN 1 ELSE 0 END) AS in_progress,
                    AVG(COALESCE(progress, 0)) AS avg_progress
                FROM tasks
                GROUP BY name
                ORDER BY total DESC
                """
            )
            return [EmployeeSummary(*row) for row in cur.fetchall()]
        finally:
            conn.close()

    def recent_reports(self, limit: int = 10) -> list[tuple]:
        conn = self._connect()
        if conn is None:
            return []
        try:
            cur = conn.execute(
                """
                SELECT report_date, overall_status, deadline_risk, summary
                FROM daily_reports
                ORDER BY report_date DESC
                LIMIT ?
                """,
                (limit,),
            )
            return cur.fetchall()
        finally:
            conn.close()
