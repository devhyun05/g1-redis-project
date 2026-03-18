from __future__ import annotations

from typing import Protocol, TypedDict

from src.protocol.parser import ERROR_TOKEN


class Store(Protocol):
    def set(self, key: str, value: str) -> None:
        ...

    def get(self, key: str) -> str | None:
        ...

    def delete(self, key: str) -> int:
        ...


class Response(TypedDict):
    type: str
    value: str | int | None


def handle_command(tokens: list[str], store: Store) -> Response:
    if not tokens:
        return _protocol_error()

    command = tokens[0]

    if command == ERROR_TOKEN:
        return _protocol_error()

    if command == "PING":
        return _handle_ping(tokens)
    if command == "SET":
        return _handle_set(tokens, store)
    if command == "GET":
        return _handle_get(tokens, store)
    if command == "DEL":
        return _handle_delete(tokens, store)

    return _error(f"ERR unknown command '{command}'")


def _handle_ping(tokens: list[str]) -> Response:
    if len(tokens) != 1:
        return _wrong_arity("PING")

    return {"type": "simple_string", "value": "PONG"}


def _handle_set(tokens: list[str], store: Store) -> Response:
    if len(tokens) != 3:
        return _wrong_arity("SET")

    _, key, value = tokens
    store.set(key, value)
    return {"type": "simple_string", "value": "OK"}


def _handle_get(tokens: list[str], store: Store) -> Response:
    if len(tokens) != 2:
        return _wrong_arity("GET")

    _, key = tokens
    value = store.get(key)
    if value is None:
        return {"type": "null", "value": None}

    return {"type": "bulk_string", "value": value}


def _handle_delete(tokens: list[str], store: Store) -> Response:
    if len(tokens) != 2:
        return _wrong_arity("DEL")

    _, key = tokens
    return {"type": "integer", "value": store.delete(key)}


def _wrong_arity(command: str) -> Response:
    return _error(f"ERR wrong number of arguments for '{command}' command")


def _protocol_error() -> Response:
    return _error("ERR protocol error")


def _error(message: str) -> Response:
    return {"type": "error", "value": message}
