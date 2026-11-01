from ama.memory.sqlite_store import SQLiteMemoryStore


def test_in_memory_store_keeps_records_between_operations():
    store = SQLiteMemoryStore(":memory:")
    record_id = store.add("cognitive event", category="event", source="test")

    assert store.get(record_id)["content"] == "cognitive event"
    assert store.search("cognitive", category="event")[0]["id"] == record_id

    store.close()
