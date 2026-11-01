"""SQLite persistence for structured knowledge facts."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ama.knowledge.models import Fact


class SQLiteKnowledgeRepository:
    """Persist facts while retaining provenance, confidence, and timestamps."""

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
                CREATE TABLE IF NOT EXISTS knowledge_facts (
                    fact_id TEXT PRIMARY KEY,
                    predicate TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
                    observed_at TEXT NOT NULL,
                    valid_until TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_knowledge_predicate "
                "ON knowledge_facts(predicate)"
            )

    def add(self, fact: Fact) -> str:
        """Save a fact. Reusing an existing fact_id raises IntegrityError."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO knowledge_facts
                    (fact_id, predicate, value_json, source, confidence,
                     observed_at, valid_until)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact.fact_id,
                    fact.predicate,
                    json.dumps(fact.value, ensure_ascii=False),
                    fact.source,
                    fact.confidence,
                    fact.observed_at,
                    fact.valid_until,
                ),
            )
        return fact.fact_id

    def get(self, fact_id: str) -> Fact | None:
        """Retrieve one fact by its stable identifier."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM knowledge_facts WHERE fact_id = ?",
                (fact_id,),
            ).fetchone()
        return self._to_fact(row) if row is not None else None

    def find(self, predicate: str | None = None, *, limit: int = 100) -> list[Fact]:
        """List facts in insertion order, optionally filtering by predicate."""
        if limit < 1:
            raise ValueError("limit must be positive")
        sql = "SELECT * FROM knowledge_facts"
        parameters: list[object] = []
        if predicate is not None:
            sql += " WHERE predicate = ?"
            parameters.append(predicate)
        sql += " ORDER BY rowid ASC LIMIT ?"
        parameters.append(limit)
        with self._connect() as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [self._to_fact(row) for row in rows]

    @staticmethod
    def _to_fact(row: sqlite3.Row) -> Fact:
        return Fact(
            fact_id=row["fact_id"],
            predicate=row["predicate"],
            value=json.loads(row["value_json"]),
            source=row["source"],
            confidence=row["confidence"],
            observed_at=row["observed_at"],
            valid_until=row["valid_until"],
        )
