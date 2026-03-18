from __future__ import annotations

import asyncio
from typing import Any, Callable


ParserFunc = Callable[[bytes], list[str]]
CommandHandlerFunc = Callable[[list[str], Any], Any]
EncoderFunc = Callable[[Any], bytes]


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
        try:
            while True:
                data = await reader.read(self.read_size)
                if not data:
                    break

                try:
                    tokens = self.parse_request(data)
                    response = self.handle_command(tokens, self.store)
                    payload = self.encode_response(response)
                except Exception:  # noqa: BLE001
                    payload = b"-ERR internal server error\r\n"

                writer.write(payload)
                try:
                    await writer.drain()
                except (BrokenPipeError, ConnectionResetError):
                    break
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionResetError:
                pass
