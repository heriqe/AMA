"""Orchestrate the structured perception-to-reasoning cognitive path."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from ama.knowledge.policy import KnowledgeAssessment, KnowledgePolicy
from ama.knowledge.sqlite_repository import SQLiteKnowledgeRepository
from ama.memory.sqlite_store import SQLiteMemoryStore
from ama.perception.normalizer import Observation, normalize_observation
from ama.reasoning.models import InferenceResult
from ama.reasoning.rules import RuleEngine


@dataclass(frozen=True, slots=True)
class CognitiveCycleResult:
    """Auditable output of one structured cognitive processing cycle."""

    observation: Observation
    knowledge_assessment: KnowledgeAssessment
    inference: InferenceResult
    memory_record_ids: tuple[int, ...]


class CognitivePipeline:
    """Connect structured perception, knowledge policy, rules, and memory.

    The pipeline intentionally accepts structured mappings only. It does not
    parse natural language, execute plans, or perform external side effects.
    """

    def __init__(
        self,
        *,
        knowledge: SQLiteKnowledgeRepository,
        memory: SQLiteMemoryStore,
        reasoning: RuleEngine,
        policy: KnowledgePolicy | None = None,
        knowledge_limit: int = 10_000,
    ) -> None:
        if knowledge_limit < 1:
            raise ValueError("knowledge_limit must be positive")
        self.knowledge = knowledge
        self.memory = memory
        self.reasoning = reasoning
        self.policy = policy or KnowledgePolicy()
        self.knowledge_limit = knowledge_limit

    def process(self, payload: Mapping[str, Any]) -> CognitiveCycleResult:
        """Persist an observation, assess known facts, infer, and log the cycle."""
        observation = normalize_observation(payload)
        fact_ids = tuple(self.knowledge.add(fact) for fact in observation.facts)

        all_facts = self.knowledge.find(limit=self.knowledge_limit)
        assessment = self.policy.assess(all_facts)
        inference = self.reasoning.infer_with_trace(assessment.as_mapping())

        records: list[int] = []
        observation_record = {
            "source": observation.source,
            "fact_ids": fact_ids,
        }
        records.append(
            self.memory.add(
                json.dumps(observation_record, ensure_ascii=False),
                category="observation",
                source=observation.source,
            )
        )

        assessment_record = {
            "assessments": [asdict(item) for item in assessment.assessments],
            "resolved": [asdict(item) for item in assessment.resolved],
        }
        records.append(
            self.memory.add(
                json.dumps(assessment_record, ensure_ascii=False, allow_nan=False),
                category="knowledge_assessment",
                source="cognitive-pipeline",
            )
        )

        for item in inference.trace:
            records.append(
                self.memory.add(
                    json.dumps(asdict(item), ensure_ascii=False, allow_nan=False),
                    category="inference",
                    source="rule-engine",
                )
            )

        return CognitiveCycleResult(
            observation=observation,
            knowledge_assessment=assessment,
            inference=inference,
            memory_record_ids=tuple(records),
        )
