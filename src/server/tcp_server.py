from __future__ import annotations

import asyncio
from typing import Any, Callable, Literal, NamedTuple


ParserFunc = Callable[[bytes], list[str]]
CommandHandlerFunc = Callable[[list[str], Any], Any]
EncoderFunc = Callable[[Any], bytes]
FrameStatus = Literal["complete", "incomplete", "malformed"]

CRLF = b"\r\n"


class _FrameExtraction(NamedTuple):
    status: FrameStatus
    frame: bytes | None = None


class TcpServer:
    """Cycle 1 runtime server: accept a connection and handle sequential requests."""

    def __init__(
        self,
        host: str,
        port: int,
        parse_request: ParserFunc,
        handle_command: CommandHandlerFunc,
        encode_response: EncoderFunc,
        store: Any,
        read_size: int = 4096,
    ) -> None:
        self.host = host
        self.port = port
        self.parse_request = parse_request
        self.handle_command = handle_command
        self.encode_response = encode_response
        self.store = store
        self.read_size = read_size
        self._server: asyncio.AbstractServer | None = None

    async def start(self) -> asyncio.AbstractServer:
        if self._server is not None:
            return self._server

        self._server = await asyncio.start_server(
            self._handle_client_session,
            host=self.host,
            port=self.port,
        )
        return self._server

    async def serve_forever(self) -> None:
        if self._server is None:
            await self.start()

        assert self._server is not None
        async with self._server:
            await self._server.serve_forever()

    async def shutdown(self) -> None:
        if self._server is None:
            return

        self._server.close()
        await self._server.wait_closed()
        self._server = None

    async def _handle_client_session(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        buffer = bytearray()

        try:
            while True:
                try:
                    data = await reader.read(self.read_size)
                except OSError:
                    break
                if not data:
                    break

                buffer.extend(data)

                # Drain every complete RESP frame currently buffered before reading again.
                while buffer:
                    extraction = _extract_request_frame(buffer)

                    if extraction.status == "incomplete":
                        break

                    if extraction.status == "malformed":
                        buffer.clear()
                        if not await _write_payload(writer, b"-ERR protocol error\r\n"):
                            return
                        break

                    assert extraction.frame is not None

                    try:
                        tokens = self.parse_request(extraction.frame)
                        response = self.handle_command(tokens, self.store)
                        payload = self.encode_response(response)
                    except Exception:  # noqa: BLE001
                        payload = b"-ERR internal server error\r\n"

                    if not await _write_payload(writer, payload):
                        return
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass


async def _write_payload(
    writer: asyncio.StreamWriter,
    payload: bytes,
) -> bool:
    writer.write(payload)

    try:
        await writer.drain()
    except (BrokenPipeError, ConnectionResetError):
        return False

    return True


def _extract_request_frame(buffer: bytearray) -> _FrameExtraction:
    if not buffer:
        return _FrameExtraction("incomplete")

    position = 0
    array_header = _read_line(buffer, position)
    if array_header is None:
        return _FrameExtraction("incomplete")

    array_line, position = array_header
    if not array_line.startswith(b"*"):
        return _FrameExtraction("malformed")

    item_count = _parse_non_negative_int(array_line[1:])
    if item_count is None or item_count == 0:
        return _FrameExtraction("malformed")

    for _ in range(item_count):
        bulk_header = _read_line(buffer, position)
        if bulk_header is None:
            return _FrameExtraction("incomplete")

        bulk_line, position = bulk_header
        if not bulk_line.startswith(b"$"):
            return _FrameExtraction("malformed")

        bulk_length = _parse_non_negative_int(bulk_line[1:])
        if bulk_length is None:
            return _FrameExtraction("malformed")

        payload_end = position + bulk_length
        if payload_end + len(CRLF) > len(buffer):
            return _FrameExtraction("incomplete")

        if buffer[payload_end:payload_end + len(CRLF)] != CRLF:
            return _FrameExtraction("malformed")

        position = payload_end + len(CRLF)

    frame = bytes(buffer[:position])
    del buffer[:position]
    return _FrameExtraction("complete", frame)


def _read_line(buffer: bytearray, position: int) -> tuple[bytes, int] | None:
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
