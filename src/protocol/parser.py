"""RESP parser for Cycle 1 protocol support."""

from __future__ import annotations

from typing import Final


ERROR_TOKEN: Final[str] = "__ERROR__"


def parse_request(data: bytes) -> list[str]:
    """Parse one RESP array-of-bulk-strings request into command tokens."""
    try:
        parser = _RequestParser(data)
        return parser.parse()
    except Exception:
        return _error_tokens("ERR protocol error")


class _RequestParser:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._position = 0

    def parse(self) -> list[str]:
        if not self._data:
            return _error_tokens("ERR protocol error")

        array_header = self._read_line()
        if array_header is None or not array_header.startswith(b"*"):
            return _error_tokens("ERR protocol error")

        item_count = _parse_non_negative_int(array_header[1:])
        if item_count is None or item_count == 0:
            return _error_tokens("ERR protocol error")

        tokens: list[str] = []
        for _ in range(item_count):
            bulk_header = self._read_line()
            if bulk_header is None or not bulk_header.startswith(b"$"):
                return _error_tokens("ERR protocol error")

            bulk_length = _parse_non_negative_int(bulk_header[1:])
            if bulk_length is None:
                return _error_tokens("ERR protocol error")

            bulk_value = self._read_exact(bulk_length)
            if bulk_value is None:
                return _error_tokens("ERR protocol error")

            if self._read_exact(2) != b"\r\n":
                return _error_tokens("ERR protocol error")

            try:
                tokens.append(bulk_value.decode("utf-8"))
            except UnicodeDecodeError:
                return _error_tokens("ERR protocol error")

        if self._position != len(self._data):
            return _error_tokens("ERR protocol error")

        tokens[0] = tokens[0].upper()
        return tokens

    def _read_line(self) -> bytes | None:
        line_end = self._data.find(b"\r\n", self._position)
        if line_end == -1:
            return None

        line = self._data[self._position:line_end]
        self._position = line_end + 2
        return line

    def _read_exact(self, length: int) -> bytes | None:
        end = self._position + length
        if end > len(self._data):
            return None

        chunk = self._data[self._position:end]
        self._position = end
        return chunk


def _parse_non_negative_int(raw_value: bytes) -> int | None:
    try:
        value = int(raw_value)
    except ValueError:
        return None

    if value < 0:
        return None

    return value


def _error_tokens(message: str) -> list[str]:
    return [ERROR_TOKEN, message]
