"""Cycle 1 minimal in-memory key-value store."""

from __future__ import annotations

import time
from typing import Protocol

from src.storage.hash_table import HashTable


class _StringValueBackend(Protocol):
    """Minimal backend contract for string key/value storage.

    Store depends on this boundary so the backing structure can change without
    affecting the server/command contract.
    """

    def set(self, key: str, value: str) -> None: ...

    def get(self, key: str) -> str | None: ...

    def delete(self, key: str) -> int: ...

    def contains(self, key: str) -> bool: ...


class _HashTableStringValueBackend:
    """HashTable adapter that preserves the existing Store contract."""

    def __init__(self) -> None:
        self._table = HashTable()

    def set(self, key: str, value: str) -> None:
        self._table.set(key, value)

    def get(self, key: str) -> str | None:
        return self._table.get(key)

    def delete(self, key: str) -> int:
        return self._table.delete(key)

    def contains(self, key: str) -> bool:
        return self._table.exists(key)


class Store:
    """Store UTF-8 string keys and values for Cycle 1."""

    def __init__(self) -> None:
        self._data: _StringValueBackend = _HashTableStringValueBackend()
        self._expire_at: dict[str, float] = {}

    def set(self, key: str, value: str) -> None:
        self._data.set(key, value)
        self._expire_at.pop(key, None)

    def get(self, key: str) -> str | None:
        self._delete_if_expired(key)
        return self._data.get(key)

    def delete(self, key: str) -> int:
        self._delete_if_expired(key)
        deleted_count = self._data.delete(key)
        if deleted_count == 1:
            self._expire_at.pop(key, None)
        return deleted_count

    def exists(self, key: str) -> bool:
        self._delete_if_expired(key)
        return self._data.contains(key)

    def expire(self, key: str, seconds: int) -> int:
        self._delete_if_expired(key)
        if not self._data.contains(key):
            return 0

        self._expire_at[key] = time.time() + seconds
        return 1

    def _delete_if_expired(self, key: str) -> None:
        expire_at = self._expire_at.get(key)
        if expire_at is None:
            return

        if expire_at <= time.time():
            self._data.delete(key)
            self._expire_at.pop(key, None)
