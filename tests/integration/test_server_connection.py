from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio

from scripts.smoke_test import encode_command
from src.commands.handler import handle_command
from src.protocol.parser import parse_request
from src.protocol.writer import encode_response
from src.server.tcp_server import TcpServer
from src.storage.store import Store


CRLF = b"\r\n"


@pytest_asyncio.fixture
async def running_server() -> tuple[str, int]:
    server = TcpServer(
        host="127.0.0.1",
        port=0,
        parse_request=parse_request,
        handle_command=handle_command,
        encode_response=encode_response,
        store=Store(),
    )

    asyncio_server = await server.start()
    sockets = asyncio_server.sockets or []
    assert sockets

    host, port = sockets[0].getsockname()[:2]

    try:
        yield host, port
    finally:
        await server.shutdown()


async def _read_response(reader: asyncio.StreamReader) -> bytes:
    prefix = await reader.readexactly(1)
    line = await reader.readuntil(CRLF)

    if prefix in {b"+", b"-", b":"}:
        return prefix + line

    if prefix == b"$":
        if line == b"-1\r\n":
            return prefix + line

        payload_length = int(line[:-2].decode("utf-8"))
        payload = await reader.readexactly(payload_length + len(CRLF))
        return prefix + line + payload

    raise RuntimeError(f"Unsupported RESP response prefix: {prefix!r}")


async def _open_connection(host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    return await asyncio.open_connection(host, port)


@pytest.mark.asyncio
async def test_single_connection_processes_multiple_requests_sequentially(
    running_server: tuple[str, int],
) -> None:
    host, port = running_server
    reader, writer = await _open_connection(host, port)

    try:
        for tokens, expected in [
            (["PING"], b"+PONG\r\n"),
            (["SET", "cycle2:key", "value"], b"+OK\r\n"),
            (["GET", "cycle2:key"], b"$5\r\nvalue\r\n"),
            (["DEL", "cycle2:key"], b":1\r\n"),
            (["GET", "cycle2:key"], b"$-1\r\n"),
        ]:
            writer.write(encode_command(tokens))
            await writer.drain()
            assert await _read_response(reader) == expected
    finally:
        writer.close()
        await writer.wait_closed()


@pytest.mark.asyncio
async def test_single_write_can_contain_multiple_requests(
    running_server: tuple[str, int],
) -> None:
    host, port = running_server
    reader, writer = await _open_connection(host, port)

    try:
        writer.write(encode_command(["PING"]) + encode_command(["PING"]))
        await writer.drain()

        assert await _read_response(reader) == b"+PONG\r\n"
        assert await _read_response(reader) == b"+PONG\r\n"
    finally:
        writer.close()
        await writer.wait_closed()


@pytest.mark.asyncio
async def test_partial_request_waits_for_remaining_bytes(
    running_server: tuple[str, int],
) -> None:
    host, port = running_server
    reader, writer = await _open_connection(host, port)
    payload = encode_command(["PING"])

    try:
        writer.write(payload[:8])
        await writer.drain()

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(_read_response(reader), timeout=0.1)

        writer.write(payload[8:])
        await writer.drain()

        assert await _read_response(reader) == b"+PONG\r\n"
    finally:
        writer.close()
        await writer.wait_closed()


@pytest.mark.asyncio
async def test_protocol_error_keeps_connection_open_and_discards_buffered_tail(
    running_server: tuple[str, int],
) -> None:
    host, port = running_server
    reader, writer = await _open_connection(host, port)

    try:
        writer.write(b"*1\r\n$bad\r\nPING\r\n" + encode_command(["PING"]))
        await writer.drain()

        assert await _read_response(reader) == b"-ERR protocol error\r\n"

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(_read_response(reader), timeout=0.1)

        writer.write(encode_command(["PING"]))
        await writer.drain()

        assert await _read_response(reader) == b"+PONG\r\n"
    finally:
        writer.close()
        await writer.wait_closed()


@pytest.mark.asyncio
async def test_client_disconnect_does_not_break_future_connections(
    running_server: tuple[str, int],
) -> None:
    host, port = running_server

    _, writer = await _open_connection(host, port)
    writer.close()
    await writer.wait_closed()
    await asyncio.sleep(0)

    reader, writer = await _open_connection(host, port)

    try:
        writer.write(encode_command(["PING"]))
        await writer.drain()

        assert await _read_response(reader) == b"+PONG\r\n"
    finally:
        writer.close()
        await writer.wait_closed()
