from ama.core.cognitive_pipeline import CognitivePipeline
from ama.knowledge.sqlite_repository import SQLiteKnowledgeRepository
from ama.memory.sqlite_store import SQLiteMemoryStore
from ama.reasoning.rules import Rule, RuleEngine


def test_pipeline_connects_perception_knowledge_reasoning_and_memory(tmp_path):
    pipeline = CognitivePipeline(
        knowledge=SQLiteKnowledgeRepository(tmp_path / "knowledge.db"),
        memory=SQLiteMemoryStore(tmp_path / "memory.db"),
        reasoning=RuleEngine(
            [
                Rule(
                    "eligible_market",
                    (("country", "BR"), ("legal", True)),
                    ("market_eligible", True),
                )
            ]
        ),
    )

    result = pipeline.process(
        {
            "source": "manual-check",
            "facts": [
                {"predicate": "country", "value": "BR", "confidence": 0.95},
                {"predicate": "legal", "value": True, "confidence": 0.9},
            ],
        }
    )

    assert result.inference.facts["market_eligible"] is True
    assert result.inference.fired_rules == ("eligible_market",)
    assert len(result.memory_record_ids) == 3
    assert len(result.knowledge_assessment.resolved) == 2


def test_pipeline_does_not_reason_from_conflicting_facts(tmp_path):
    pipeline = CognitivePipeline(
        knowledge=SQLiteKnowledgeRepository(tmp_path / "knowledge.db"),
        memory=SQLiteMemoryStore(tmp_path / "memory.db"),
        reasoning=RuleEngine(
            [Rule("market_rule", (("country", "BR"),), ("eligible", True))]
        ),
    )

    pipeline.process(
        {"source": "source-a", "facts": [{"predicate": "country", "value": "BR"}]}
    )
    result = pipeline.process(
        {"source": "source-b", "facts": [{"predicate": "country", "value": "US"}]}
    )

    assert "country" not in result.inference.facts
    assert "eligible" not in result.inference.facts
    assert {item.status for item in result.knowledge_assessment.assessments} == {"conflict"}
