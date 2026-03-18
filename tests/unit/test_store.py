import pytest

from src.storage.hash_table import HashTable
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


def test_store_uses_hash_table_backing() -> None:
    store = Store()

    assert isinstance(store._data._table, HashTable)


def test_delete_removes_existing_key_and_returns_one() -> None:
    store = Store()
    store.set("name", "redis")

    deleted_count = store.delete("name")

    assert deleted_count == 1
    assert store.get("name") is None


def test_delete_returns_zero_for_missing_key() -> None:
    store = Store()

    assert store.delete("missing") == 0


def test_exists_returns_false_for_missing_key() -> None:
    store = Store()

    assert store.exists("missing") is False


def test_exists_returns_true_for_existing_key() -> None:
    store = Store()
    store.set("name", "redis")

    assert store.exists("name") is True


def test_expire_returns_zero_for_missing_key() -> None:
    store = Store()

    assert store.expire("missing", 3) == 0


def test_expire_keeps_value_available_before_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    store = Store()
    monkeypatch.setattr("src.storage.store.time.time", lambda: 100.0)
    store.set("session", "abc123")

    assert store.expire("session", 3) == 1

    monkeypatch.setattr("src.storage.store.time.time", lambda: 102.0)
    assert store.get("session") == "abc123"


def test_get_returns_none_after_expiration(monkeypatch: pytest.MonkeyPatch) -> None:
    store = Store()
    monkeypatch.setattr("src.storage.store.time.time", lambda: 100.0)
    store.set("session", "abc123")
    store.expire("session", 3)

    monkeypatch.setattr("src.storage.store.time.time", lambda: 104.0)
    assert store.get("session") is None


def test_exists_returns_false_after_expiration(monkeypatch: pytest.MonkeyPatch) -> None:
    store = Store()
    monkeypatch.setattr("src.storage.store.time.time", lambda: 100.0)
    store.set("session", "abc123")
    store.expire("session", 3)

    monkeypatch.setattr("src.storage.store.time.time", lambda: 104.0)
    assert store.exists("session") is False


def test_delete_returns_zero_for_expired_key(monkeypatch: pytest.MonkeyPatch) -> None:
    store = Store()
    monkeypatch.setattr("src.storage.store.time.time", lambda: 100.0)
    store.set("session", "abc123")
    store.expire("session", 3)

    monkeypatch.setattr("src.storage.store.time.time", lambda: 104.0)
    assert store.delete("session") == 0


def test_set_clears_existing_expiration(monkeypatch: pytest.MonkeyPatch) -> None:
    store = Store()
    monkeypatch.setattr("src.storage.store.time.time", lambda: 100.0)
    store.set("session", "first")
    store.expire("session", 3)

    monkeypatch.setattr("src.storage.store.time.time", lambda: 101.0)
    store.set("session", "second")

    monkeypatch.setattr("src.storage.store.time.time", lambda: 110.0)
    assert store.get("session") == "second"


def test_store_preserves_values_across_hash_table_resize() -> None:
    store = Store()

    for index in range(12):
        store.set(f"key-{index}", f"value-{index}")

    for index in range(12):
        assert store.get(f"key-{index}") == f"value-{index}"
