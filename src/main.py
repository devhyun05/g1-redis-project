from __future__ import annotations

import asyncio
import os
from pathlib import Path

from src.commands.handler import handle_command
from src.protocol.parser import parse_request
from src.protocol.writer import encode_response
from src.server.tcp_server import TcpServer
from src.storage.store import Store


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 6379
DEFAULT_READ_BUFFER_SIZE = 4096

ENV_HOST_KEY = "REDIS_HOST"
ENV_PORT_KEY = "REDIS_PORT"
ENV_READ_BUFFER_SIZE_KEY = "READ_BUFFER_SIZE"


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def load_server_config() -> tuple[str, int, int]:
    host = os.getenv(ENV_HOST_KEY, DEFAULT_HOST).strip() or DEFAULT_HOST
    port = _load_int_env(ENV_PORT_KEY, DEFAULT_PORT)
    read_buffer_size = _load_int_env(ENV_READ_BUFFER_SIZE_KEY, DEFAULT_READ_BUFFER_SIZE)
    return host, port, read_buffer_size


def _load_int_env(key: str, default: int) -> int:
    raw_value = os.getenv(key, str(default)).strip()
    try:
        return int(raw_value)
    except ValueError:
        return default


async def run_server() -> None:
    load_dotenv()
    host, port, read_buffer_size = load_server_config()

    server = TcpServer(
        host=host,
        port=port,
        parse_request=parse_request,
        handle_command=handle_command,
        encode_response=encode_response,
        store=Store(),
        read_size=read_buffer_size,
    )

    await server.start()
    print(f"Mini Redis server listening on {host}:{port}")
    try:
        await server.serve_forever()
    finally:
        await server.shutdown()


def main() -> None:
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("Mini Redis server stopped")


if __name__ == "__main__":
    main()
