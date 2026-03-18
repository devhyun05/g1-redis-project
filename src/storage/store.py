"""Cycle 1 minimal in-memory key-value store."""

from __future__ import annotations

import time


class Store:
    """Store UTF-8 string keys and values for Cycle 1."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._expire_at: dict[str, float] = {}

    def set(self, key: str, value: str) -> None:
        self._data[key] = value
        self._expire_at.pop(key, None)

    def get(self, key: str) -> str | None:
        self._delete_if_expired(key)
        return self._data.get(key)

    def delete(self, key: str) -> int:
        self._delete_if_expired(key)
        if key in self._data:
            del self._data[key]
            self._expire_at.pop(key, None)
            return 1
        return 0

    def expire(self, key: str, seconds: int) -> int:
        self._delete_if_expired(key)
        if key not in self._data:
            return 0

        self._expire_at[key] = time.time() + seconds
        return 1

    def _delete_if_expired(self, key: str) -> None:
        expire_at = self._expire_at.get(key)
        if expire_at is None:
            return

        if expire_at <= time.time():
            self._data.pop(key, None)
            self._expire_at.pop(key, None)
