import importlib

import pytest

from src.storage.store import Store
from src.protocol.parser import ERROR_TOKEN


handler_module = importlib.import_module("src.commands.handler")
handle_command = getattr(handler_module, "handle_command", None)

pytestmark = pytest.mark.skipif(
    not callable(handle_command),
    reason="handle_command is not implemented yet",
)


def test_ping_returns_pong_response() -> None:
    store = Store()

    result = handle_command(["PING"], store)

    assert result == {"type": "simple_string", "value": "PONG"}


def test_set_get_and_del_follow_cycle_1_contract() -> None:
    store = Store()

    assert handle_command(["SET", "mykey", "value"], store) == {
        "type": "simple_string",
        "value": "OK",
    }
    assert handle_command(["GET", "mykey"], store) == {
        "type": "bulk_string",
        "value": "value",
    }
    assert handle_command(["DEL", "mykey"], store) == {
        "type": "integer",
        "value": 1,
    }
    assert handle_command(["GET", "mykey"], store) == {
        "type": "null",
        "value": None,
    }


def test_del_returns_zero_when_key_is_missing() -> None:
    store = Store()

    result = handle_command(["DEL", "missing"], store)

    assert result == {"type": "integer", "value": 0}


def test_unknown_command_returns_error_response() -> None:
    store = Store()

    result = handle_command(["BOGUS"], store)

    assert result == {"type": "error", "value": "ERR unknown command 'BOGUS'"}


@pytest.mark.parametrize(
    ("tokens", "expected_message"),
    [
        (["PING", "extra"], "ERR wrong number of arguments for 'PING' command"),
        (["SET", "key"], "ERR wrong number of arguments for 'SET' command"),
        (["GET"], "ERR wrong number of arguments for 'GET' command"),
        (["DEL", "key", "extra"], "ERR wrong number of arguments for 'DEL' command"),
    ],
)
def test_wrong_arity_returns_error_response(
    tokens: list[str],
    expected_message: str,
) -> None:
    store = Store()

    result = handle_command(tokens, store)

    assert result == {"type": "error", "value": expected_message}


def test_protocol_error_token_returns_protocol_error_response() -> None:
    store = Store()

    result = handle_command([ERROR_TOKEN, "ERR protocol error"], store)

    assert result == {"type": "error", "value": "ERR protocol error"}
