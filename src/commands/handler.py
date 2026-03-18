from __future__ import annotations

from typing import Protocol, TypedDict, runtime_checkable

from src.protocol.parser import ERROR_TOKEN


@runtime_checkable
class StoreProtocol(Protocol):
    def set(self, key: str, value: str) -> None:
        ...

    def get(self, key: str) -> str | None:
        ...

    def delete(self, key: str) -> int:
        ...

    def expire(self, key: str, seconds: int) -> int:
        ...


class Response(TypedDict):
    type: str
    value: str | int | None


def handle_command(tokens: list[str], store: StoreProtocol) -> Response:
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
    if command == "EXISTS":
        return _handle_exists(tokens, store)
    if command == "INCR":
        return _handle_increment(tokens, store, delta=1)
    if command == "DECR":
        return _handle_increment(tokens, store, delta=-1)
    if command == "EXPIRE":
        return _handle_expire(tokens, store)

    return _error(f"ERR unknown command '{command}'")


def _handle_ping(tokens: list[str]) -> Response:
    if len(tokens) != 1:
        return _wrong_arity("PING")

    return {"type": "simple_string", "value": "PONG"}


def _handle_set(tokens: list[str], store: StoreProtocol) -> Response:
    if len(tokens) != 3:
        return _wrong_arity("SET")

    _, key, value = tokens
    store.set(key, value)
    return {"type": "simple_string", "value": "OK"}


def _handle_get(tokens: list[str], store: StoreProtocol) -> Response:
    if len(tokens) != 2:
        return _wrong_arity("GET")

    _, key = tokens
    value = store.get(key)
    if value is None:
        return {"type": "null", "value": None}

    return {"type": "bulk_string", "value": value}


def _handle_delete(tokens: list[str], store: StoreProtocol) -> Response:
    if len(tokens) != 2:
        return _wrong_arity("DEL")

    _, key = tokens
    return {"type": "integer", "value": store.delete(key)}


def _handle_exists(tokens: list[str], store: StoreProtocol) -> Response:
    if len(tokens) != 2:
        return _wrong_arity("EXISTS")

    _, key = tokens
    return {"type": "integer", "value": 1 if _store_exists(store, key) else 0}


def _handle_increment(tokens: list[str], store: StoreProtocol, delta: int) -> Response:
    command = "INCR" if delta > 0 else "DECR"
    if len(tokens) != 2:
        return _wrong_arity(command)

    _, key = tokens
    raw_value = store.get(key)
    if raw_value is None:
        current_value = 0
    else:
        try:
            current_value = int(raw_value)
        except ValueError:
            return _error(f"ERR value is not an integer or out of range for '{command}'")

    next_value = current_value + delta
    store.set(key, str(next_value))
    return {"type": "integer", "value": next_value}


def _handle_expire(tokens: list[str], store: StoreProtocol) -> Response:
    if len(tokens) != 3:
        return _wrong_arity("EXPIRE")

    _, key, raw_seconds = tokens
    try:
        seconds = int(raw_seconds)
    except ValueError:
        return _error("ERR value is not an integer or out of range for 'EXPIRE'")

    return {"type": "integer", "value": store.expire(key, seconds)}


def _store_exists(store: StoreProtocol, key: str) -> bool:
    exists = getattr(store, "exists", None)
    if callable(exists):
        return bool(exists(key))

    return store.get(key) is not None


def _wrong_arity(command: str) -> Response:
    return _error(f"ERR wrong number of arguments for '{command}' command")


def _protocol_error() -> Response:
    return _error("ERR protocol error")


def _error(message: str) -> Response:
    return {"type": "error", "value": message}
