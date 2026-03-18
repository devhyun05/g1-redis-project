"""Custom hash table implementation for Cycle 3 storage work."""

from __future__ import annotations

from dataclasses import dataclass


INITIAL_BUCKET_COUNT = 8
MAX_LOAD_FACTOR = 0.75
FNV_64_OFFSET_BASIS = 14695981039346656037
FNV_64_PRIME = 1099511628211


@dataclass(slots=True)
class HashNode:
    key: str
    value: str
    next: HashNode | None = None


class HashTable:
    """Store UTF-8 string keys and values using separate chaining."""

    def __init__(self) -> None:
        self._buckets: list[HashNode | None] = [None] * INITIAL_BUCKET_COUNT
        self._size = 0

    def set(self, key: str, value: str) -> None:
        existing_node = self._find_node(key)
        if existing_node is not None:
            existing_node.value = value
            return

        if (self._size + 1) / len(self._buckets) > MAX_LOAD_FACTOR:
            self._resize()

        bucket_index = self._index_for(key)
        self._buckets[bucket_index] = HashNode(
            key=key,
            value=value,
            next=self._buckets[bucket_index],
        )
        self._size += 1

    def get(self, key: str) -> str | None:
        node = self._find_node(key)
        if node is None:
            return None
        return node.value

    def delete(self, key: str) -> int:
        bucket_index = self._index_for(key)
        current = self._buckets[bucket_index]
        previous: HashNode | None = None

        while current is not None:
            if current.key == key:
                if previous is None:
                    self._buckets[bucket_index] = current.next
                else:
                    previous.next = current.next
                self._size -= 1
                return 1
            previous = current
            current = current.next

        return 0

    def exists(self, key: str) -> bool:
        return self._find_node(key) is not None

    def _find_node(self, key: str) -> HashNode | None:
        bucket_index = self._index_for(key)
        current = self._buckets[bucket_index]

        while current is not None:
            if current.key == key:
                return current
            current = current.next

        return None

    def _hash(self, key: str) -> int:
        hashed_value = FNV_64_OFFSET_BASIS
        for byte in key.encode("utf-8"):
            hashed_value ^= byte
            hashed_value = (hashed_value * FNV_64_PRIME) & 0xFFFFFFFFFFFFFFFF
        return hashed_value

    def _index_for(self, key: str, bucket_count: int | None = None) -> int:
        target_bucket_count = bucket_count or len(self._buckets)
        return self._hash(key) % target_bucket_count

    def _resize(self) -> None:
        self._buckets = self._rehash_into_new_buckets(len(self._buckets) * 2)

    def _rehash_into_new_buckets(self, bucket_count: int) -> list[HashNode | None]:
        new_buckets: list[HashNode | None] = [None] * bucket_count

        for bucket in self._buckets:
            current = bucket
            while current is not None:
                new_index = self._index_for(current.key, bucket_count)
                new_buckets[new_index] = HashNode(
                    key=current.key,
                    value=current.value,
                    next=new_buckets[new_index],
                )
                current = current.next

        return new_buckets
