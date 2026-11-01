from ama.memory.sqlite_store import SQLiteMemoryStore


def test_add_get_and_search_records(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")

    record_id = store.add(
        "AMA foundation created",
        category="milestone",
        source="test",
    )

    record = store.get(record_id)
    assert record is not None
    assert record["content"] == "AMA foundation created"
    assert record["category"] == "milestone"

    results = store.search("foundation", category="milestone")
    assert len(results) == 1
    assert results[0]["id"] == record_id


def test_empty_content_is_rejected(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")

    try:
        store.add("   ")
    except ValueError as error:
        assert "content" in str(error)
    else:
        raise AssertionError("Expected ValueError")
