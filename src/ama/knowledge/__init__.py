"""Structured knowledge representation and persistence for AMA."""

from ama.knowledge.models import Fact
from ama.knowledge.sqlite_repository import SQLiteKnowledgeRepository

__all__ = ["Fact", "SQLiteKnowledgeRepository"]
