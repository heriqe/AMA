"""Small SQLite-backed record store for the AMA foundation.

This is persistence, not an autonomous learning mechanism.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SQLiteMemoryStore:
    """Store and retrieve simple categorized text records."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_category "
                "ON memory_records(category)"
            )

    def add(
        self,
        content: str,
        *,
        category: str = "general",
        source: str = "unknown",
    ) -> int:
        """Persist a record and return its database identifier."""
        if not content.strip():
            raise ValueError("content must not be empty")
        if not category.strip() or not source.strip():
            raise ValueError("category and source must not be empty")

        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO memory_records(category, content, source, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (category, content, source, created_at),
            )
            return int(cursor.lastrowid)

    def get(self, record_id: int) -> dict[str, Any] | None:
        """Return one record, or None when it does not exist."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM memory_records WHERE id = ?",
                (record_id,),
            ).fetchone()
        return dict(row) if row is not None else None

    def search(
        self,
        query: str = "",
        *,
        category: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search records using a parameterized literal substring query."""
        if limit < 1:
            raise ValueError("limit must be positive")

        sql = "SELECT * FROM memory_records WHERE 1 = 1"
        parameters: list[Any] = []

        if query:
            sql += " AND instr(content, ?) > 0"
            parameters.append(query)
        if category is not None:
            sql += " AND category = ?"
            parameters.append(category)

        sql += " ORDER BY id DESC LIMIT ?"
        parameters.append(limit)

        with self._connect() as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [dict(row) for row in rows]
