from __future__ import annotations

from src.storage.hash_table import HashTable


def test_missing_key_returns_empty_results() -> None:
    table = HashTable()

    assert table.get("missing") is None
    assert table.delete("missing") == 0
    assert table.exists("missing") is False


def test_set_get_and_overwrite_value() -> None:
    table = HashTable()

    table.set("name", "redis")
    assert table.get("name") == "redis"
    assert table.exists("name") is True

    table.set("name", "mini-redis")
    assert table.get("name") == "mini-redis"


def test_collision_keys_remain_accessible_after_deleting_head() -> None:
    table = HashTable()
    first, second, third = _find_colliding_keys(table, count=3)

    table.set(first, "v1")
    table.set(second, "v2")
    table.set(third, "v3")

    assert table.delete(third) == 1
    assert table.get(third) is None
    assert table.get(first) == "v1"
    assert table.get(second) == "v2"


def test_collision_keys_remain_accessible_after_deleting_middle() -> None:
    table = HashTable()
    first, second, third = _find_colliding_keys(table, count=3)

    table.set(first, "v1")
    table.set(second, "v2")
    table.set(third, "v3")

    assert table.delete(second) == 1
    assert table.get(second) is None
    assert table.get(first) == "v1"
    assert table.get(third) == "v3"


def test_collision_keys_remain_accessible_after_deleting_tail() -> None:
    table = HashTable()
    first, second, third = _find_colliding_keys(table, count=3)

    table.set(first, "v1")
    table.set(second, "v2")
    table.set(third, "v3")

    assert table.delete(first) == 1
    assert table.get(first) is None
    assert table.get(second) == "v2"
    assert table.get(third) == "v3"


def test_resize_preserves_existing_values_after_seventh_insert() -> None:
    table = HashTable()

    for index in range(7):
        table.set(f"key-{index}", f"value-{index}")

    assert len(table._buckets) == 16

    for index in range(7):
        assert table.get(f"key-{index}") == f"value-{index}"


def test_index_calculation_is_deterministic_for_same_key() -> None:
    first_table = HashTable()
    second_table = HashTable()

    first_index = first_table._index_for("stable-key")
    second_index = first_table._index_for("stable-key")

    assert first_index == second_index
    assert second_index == second_table._index_for("stable-key")


def _find_colliding_keys(table: HashTable, count: int) -> list[str]:
    collisions_by_index: dict[int, list[str]] = {}
    candidate = 0

    while True:
        key = f"collision-{candidate}"
        bucket_index = table._index_for(key)
        collisions = collisions_by_index.setdefault(bucket_index, [])
        collisions.append(key)

        if len(collisions) == count:
            return collisions

        candidate += 1
