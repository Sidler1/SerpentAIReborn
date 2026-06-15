"""SQLite-backed analytics event store (replaces the pony/sqlite dashboard models).

Plain stdlib ``sqlite3`` — no ORM. A connection is opened per operation so the
store is safe to use from FastAPI's worker threads and a background consumer
thread concurrently (SQLite serialises writes; reads are concurrent).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = "dashboard/analytics.sqlite"


class EventStore:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_key TEXT,
                    event_key TEXT,
                    data TEXT,
                    timestamp TEXT,
                    is_persistable INTEGER DEFAULT 1
                )
                """
            )

    def record_event(self, event: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO events (project_key, event_key, data, timestamp, is_persistable) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    event.get("project_key"),
                    event.get("event_key"),
                    json.dumps(event.get("data")),
                    event.get("timestamp"),
                    int(bool(event.get("is_persistable", True))),
                ),
            )

    def recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT project_key, event_key, data, timestamp FROM events "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()

        return [
            {
                "project_key": row["project_key"],
                "event_key": row["event_key"],
                "data": json.loads(row["data"]) if row["data"] is not None else None,
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    def event_counts(self) -> dict[str, int]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT event_key, COUNT(*) AS n FROM events GROUP BY event_key ORDER BY n DESC"
            ).fetchall()

        return {row["event_key"]: row["n"] for row in rows}

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM events")
