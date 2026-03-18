"""RESP response encoder for Cycle 1 protocol support."""

from __future__ import annotations

from typing import Literal, TypedDict


ResponseType = Literal["simple_string", "bulk_string", "integer", "null", "error"]


class Response(TypedDict):
    type: ResponseType
    value: str | int | None


def encode_response(response: Response) -> bytes:
    response_type = response["type"]
    value = response["value"]

    if response_type == "simple_string":
        if not isinstance(value, str):
            raise TypeError("simple_string response value must be str")
        return f"+{value}\r\n".encode("utf-8")

    if response_type == "bulk_string":
        if not isinstance(value, str):
            raise TypeError("bulk_string response value must be str")
        encoded_value = value.encode("utf-8")
        return f"${len(encoded_value)}\r\n".encode("ascii") + encoded_value + b"\r\n"

    if response_type == "integer":
        if not isinstance(value, int):
            raise TypeError("integer response value must be int")
        return f":{value}\r\n".encode("ascii")

    if response_type == "null":
        if value is not None:
            raise TypeError("null response value must be None")
        return b"$-1\r\n"

    if response_type == "error":
        if not isinstance(value, str):
            raise TypeError("error response value must be str")
        return f"-{value}\r\n".encode("utf-8")

    raise ValueError(f"unsupported response type: {response_type}")
