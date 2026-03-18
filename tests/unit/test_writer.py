import pytest

from src.protocol.writer import encode_response


def test_encode_response_serializes_simple_string() -> None:
    assert encode_response({"type": "simple_string", "value": "PONG"}) == b"+PONG\r\n"


def test_encode_response_serializes_bulk_string() -> None:
    assert encode_response({"type": "bulk_string", "value": "value"}) == b"$5\r\nvalue\r\n"


def test_encode_response_serializes_integer() -> None:
    assert encode_response({"type": "integer", "value": 1}) == b":1\r\n"


def test_encode_response_serializes_null() -> None:
    assert encode_response({"type": "null", "value": None}) == b"$-1\r\n"


def test_encode_response_serializes_error() -> None:
    assert encode_response({"type": "error", "value": "ERR boom"}) == b"-ERR boom\r\n"


@pytest.mark.parametrize(
    ("response", "expected_error"),
    [
        ({"type": "simple_string", "value": 1}, TypeError),
        ({"type": "bulk_string", "value": None}, TypeError),
        ({"type": "integer", "value": "1"}, TypeError),
        ({"type": "null", "value": "x"}, TypeError),
        ({"type": "error", "value": 0}, TypeError),
        ({"type": "bogus", "value": "x"}, ValueError),
    ],
)
def test_encode_response_rejects_invalid_response_shapes(
    response: dict[str, object],
    expected_error: type[Exception],
) -> None:
    with pytest.raises(expected_error):
        encode_response(response)  # type: ignore[arg-type]
