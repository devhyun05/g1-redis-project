"""Cycle 1 minimal in-memory key-value store."""


class Store:
    """Store UTF-8 string keys and values for Cycle 1."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def delete(self, key: str) -> int:
        if key in self._data:
            del self._data[key]
            return 1
        return 0
