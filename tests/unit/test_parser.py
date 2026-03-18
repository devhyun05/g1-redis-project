from src.protocol.parser import ERROR_TOKEN, parse_request


def test_parse_request_returns_tokens_for_valid_resp_array() -> None:
    payload = b"*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n"

    assert parse_request(payload) == ["GET", "key"]


def test_parse_request_normalizes_command_to_uppercase() -> None:
    payload = b"*1\r\n$4\r\nping\r\n"

    assert parse_request(payload) == ["PING"]


def test_parse_request_returns_protocol_error_for_invalid_array_header() -> None:
    payload = b"+PING\r\n"

    assert parse_request(payload) == [ERROR_TOKEN, "ERR protocol error"]


def test_parse_request_returns_protocol_error_for_invalid_bulk_length() -> None:
    payload = b"*1\r\n$bad\r\nPING\r\n"

    assert parse_request(payload) == [ERROR_TOKEN, "ERR protocol error"]


def test_parse_request_returns_protocol_error_for_truncated_payload() -> None:
    payload = b"*2\r\n$3\r\nGET\r\n$5\r\nkey\r\n"

    assert parse_request(payload) == [ERROR_TOKEN, "ERR protocol error"]


def test_parse_request_returns_protocol_error_for_trailing_garbage() -> None:
    payload = b"*1\r\n$4\r\nPING\r\njunk"

    assert parse_request(payload) == [ERROR_TOKEN, "ERR protocol error"]


def test_parse_request_returns_protocol_error_for_invalid_utf8() -> None:
    payload = b"*1\r\n$2\r\n\xff\xfe\r\n"

    assert parse_request(payload) == [ERROR_TOKEN, "ERR protocol error"]
