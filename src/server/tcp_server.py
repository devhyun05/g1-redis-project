from __future__ import annotations

import asyncio
import itertools
import json
import logging
import time
from typing import Any, Callable, Literal, NamedTuple


ParserFunc = Callable[[bytes], list[str]]
CommandHandlerFunc = Callable[[list[str], Any], Any]
EncoderFunc = Callable[[Any], bytes]
PersistCommandFunc = Callable[[list[str], Any], None]
RecordRequestFunc = Callable[[list[str]], None]
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
        persist_command: PersistCommandFunc | None = None,
        record_request: RecordRequestFunc | None = None,
        read_size: int = 4096,
        log_requests: bool = True,
        logger: logging.Logger | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.parse_request = parse_request
        self.handle_command = handle_command
        self.encode_response = encode_response
        self.store = store
        self.persist_command = persist_command
        self.record_request = record_request
        self.read_size = read_size
        self.log_requests = log_requests
        self.logger = logger or logging.getLogger("mini_redis.server")
        self._server: asyncio.AbstractServer | None = None
        self._connection_counter = itertools.count(1)

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
        connection_id = next(self._connection_counter)
        client = _format_client(writer.get_extra_info("peername"))
        request_count = 0

        self._log_event(
            "connection_open",
            connection_id=connection_id,
            client=client,
        )

        try:
            while True:
                try:
                    data = await reader.read(self.read_size)
                except OSError:
                    self._log_event(
                        "connection_read_error",
                        connection_id=connection_id,
                        client=client,
                    )
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
                        self._log_event(
                            "protocol_error",
                            connection_id=connection_id,
                            client=client,
                        )
                        if not await _write_payload(writer, b"-ERR protocol error\r\n"):
                            return
                        break

                    assert extraction.frame is not None
                    request_count += 1
                    started_at = time.perf_counter()
                    response_type = "error"
                    tokens: list[str] = []

                    try:
                        tokens = self.parse_request(extraction.frame)
                        if self.record_request is not None:
                            self.record_request(tokens)
                        response = self.handle_command(tokens, self.store)
                        if isinstance(response, dict):
                            response_type = str(response.get("type", "unknown"))
                        else:
                            response_type = "unknown"
                        payload = self.encode_response(response)
                    except Exception:  # noqa: BLE001
                        payload = b"-ERR internal server error\r\n"
                    else:
                        if self.persist_command is not None:
                            try:
                                self.persist_command(tokens, response)
                            except Exception:  # noqa: BLE001
                                response_type = "error"
                                payload = b"-ERR internal server error\r\n"

                    if self.log_requests:
                        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 3)
                        self._log_event(
                            "request",
                            connection_id=connection_id,
                            client=client,
                            request_index=request_count,
                            command=_command_name(tokens),
                            argc=len(tokens),
                            key=_command_key(tokens),
                            response_type=response_type,
                            payload_bytes=len(extraction.frame),
                            latency_ms=elapsed_ms,
                        )

                    if not await _write_payload(writer, payload):
                        return
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass
            self._log_event(
                "connection_close",
                connection_id=connection_id,
                client=client,
                request_count=request_count,
            )

    def _log_event(self, event: str, **fields: Any) -> None:
        payload = {"event": event, **fields}
        self.logger.info(json.dumps(payload, separators=(",", ":")))


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


def _command_name(tokens: list[str]) -> str:
    if not tokens:
        return "UNKNOWN"

    return tokens[0]


def _command_key(tokens: list[str]) -> str | None:
    if len(tokens) < 2:
        return None

    return tokens[1]


def _format_client(peername: Any) -> str:
    if isinstance(peername, tuple) and len(peername) >= 2:
        return f"{peername[0]}:{peername[1]}"

    if peername is None:
        return "unknown"

    return str(peername)
