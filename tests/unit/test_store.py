from src.storage.store import Store


def test_get_returns_none_for_missing_key() -> None:
    store = Store()

    assert store.get("missing") is None


def test_set_stores_value_for_key() -> None:
    store = Store()

    store.set("name", "redis")

    assert store.get("name") == "redis"


def test_set_overwrites_existing_value() -> None:
    store = Store()
    store.set("name", "first")

    store.set("name", "second")

    assert store.get("name") == "second"


def test_delete_removes_existing_key_and_returns_one() -> None:
    store = Store()
    store.set("name", "redis")

    deleted_count = store.delete("name")

    assert deleted_count == 1
    assert store.get("name") is None


def test_delete_returns_zero_for_missing_key() -> None:
    store = Store()

    assert store.delete("missing") == 0
