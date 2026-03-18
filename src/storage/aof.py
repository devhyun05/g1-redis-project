"""Append-only file persistence for mutating Redis-like commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


CRLF = b"\r\n"
MUTATING_COMMANDS = {"SET", "DEL", "INCR", "DECR"}


class AppendOnlyFile:
    """Persist mutating commands and replay them on startup."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def append(self, tokens: list[str]) -> None:
        if not tokens or tokens[0] not in MUTATING_COMMANDS:
            return

        payload = encode_command(tokens)
        with self._path.open("ab") as file:
            file.write(payload)
            file.flush()

    def replay(
        self,
        store: object,
        command_handler: Callable[[list[str], object], dict[str, Any]],
    ) -> None:
        if not self._path.exists():
            return

        raw_data = self._path.read_bytes()
        buffer = bytearray(raw_data)

        while buffer:
            frame = _extract_request_frame(buffer)
            if frame is None:
                raise ValueError("AOF contains an incomplete RESP frame")

            tokens = parse_command_frame(frame)
            response = command_handler(tokens, store)
            if response["type"] == "error":
                raise ValueError(f"AOF replay failed for command: {tokens[0]}")


def encode_command(tokens: list[str]) -> bytes:
    parts = [f"*{len(tokens)}\r\n".encode("utf-8")]

    for token in tokens:
        encoded = token.encode("utf-8")
        parts.append(f"${len(encoded)}\r\n".encode("utf-8"))
        parts.append(encoded + CRLF)

    return b"".join(parts)


def parse_command_frame(frame: bytes) -> list[str]:
    position = 0
    array_header, position = _read_line(frame, position)
    item_count = int(array_header[1:])
    tokens: list[str] = []

    for _ in range(item_count):
        bulk_header, position = _read_line(frame, position)
        bulk_length = int(bulk_header[1:])
        bulk_value = frame[position:position + bulk_length]
        position += bulk_length + len(CRLF)
        tokens.append(bulk_value.decode("utf-8"))

    tokens[0] = tokens[0].upper()
    return tokens


def _extract_request_frame(buffer: bytearray) -> bytes | None:
    position = 0
    header = _read_line_from_buffer(buffer, position)
    if header is None:
        return None

    array_line, position = header
    if not array_line.startswith(b"*"):
        raise ValueError("AOF contains a malformed RESP array")

    item_count = _parse_non_negative_int(array_line[1:])
    if item_count is None or item_count == 0:
        raise ValueError("AOF contains an invalid array length")

    for _ in range(item_count):
        bulk_header = _read_line_from_buffer(buffer, position)
        if bulk_header is None:
            return None

        bulk_line, position = bulk_header
        if not bulk_line.startswith(b"$"):
            raise ValueError("AOF contains a malformed bulk string header")

        bulk_length = _parse_non_negative_int(bulk_line[1:])
        if bulk_length is None:
            raise ValueError("AOF contains an invalid bulk string length")

        payload_end = position + bulk_length
        if payload_end + len(CRLF) > len(buffer):
            return None

        if buffer[payload_end:payload_end + len(CRLF)] != CRLF:
            raise ValueError("AOF contains an invalid bulk string terminator")

        position = payload_end + len(CRLF)

    frame = bytes(buffer[:position])
    del buffer[:position]
    return frame


def _read_line(payload: bytes, position: int) -> tuple[bytes, int]:
    line_end = payload.find(CRLF, position)
    if line_end == -1:
        raise ValueError("RESP frame is missing CRLF")

    return payload[position:line_end], line_end + len(CRLF)


def _read_line_from_buffer(buffer: bytearray, position: int) -> tuple[bytes, int] | None:
    line_end = buffer.find(CRLF, position)
    if line_end == -1:
        return None

    return bytes(buffer[position:line_end]), line_end + len(CRLF)


def _parse_non_negative_int(raw_value: bytes) -> int | None:
    try:
        value = int(raw_value)
    except ValueError:
        return None

    if value < 0:
        return None

    return value
