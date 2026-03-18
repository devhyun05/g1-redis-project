from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Callable

from src.commands.handler import handle_command
from src.protocol.parser import parse_request
from src.protocol.writer import encode_response
from src.server.tcp_server import TcpServer
from src.storage.aof import AppendOnlyFile, MUTATING_COMMANDS
from src.storage.store import Store


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 6379
DEFAULT_READ_BUFFER_SIZE = 4096

ENV_HOST_KEY = "REDIS_HOST"
ENV_PORT_KEY = "REDIS_PORT"
ENV_READ_BUFFER_SIZE_KEY = "READ_BUFFER_SIZE"
ENV_AOF_ENABLED_KEY = "AOF_ENABLED"
ENV_AOF_PATH_KEY = "AOF_PATH"


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


def load_server_config() -> tuple[str, int, int, bool, Path]:
    host = os.getenv(ENV_HOST_KEY, DEFAULT_HOST).strip() or DEFAULT_HOST
    port = _load_int_env(ENV_PORT_KEY, DEFAULT_PORT)
    read_buffer_size = _load_int_env(ENV_READ_BUFFER_SIZE_KEY, DEFAULT_READ_BUFFER_SIZE)
    aof_enabled = _load_bool_env(ENV_AOF_ENABLED_KEY, default=False)
    aof_path = Path(os.getenv(ENV_AOF_PATH_KEY, "data/appendonly.aof"))
    return host, port, read_buffer_size, aof_enabled, aof_path


def _load_int_env(key: str, default: int) -> int:
    raw_value = os.getenv(key, str(default)).strip()
    try:
        return int(raw_value)
    except ValueError:
        return default


def _load_bool_env(key: str, default: bool) -> bool:
    raw_value = os.getenv(key, "true" if default else "false").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


async def run_server() -> None:
    load_dotenv()
    host, port, read_buffer_size, aof_enabled, aof_path = load_server_config()
    store = Store()
    aof = AppendOnlyFile(aof_path) if aof_enabled else None

    if aof is not None:
        aof.replay(store, handle_command)

    server = TcpServer(
        host=host,
        port=port,
        parse_request=parse_request,
        handle_command=handle_command,
        encode_response=encode_response,
        store=store,
        persist_command=_persist_command(aof),
        read_size=read_buffer_size,
    )

    await server.start()
    print(f"Mini Redis server listening on {host}:{port}")
    try:
        await server.serve_forever()
    finally:
        await server.shutdown()


def _persist_command(aof: AppendOnlyFile | None) -> Callable[[list[str], Any], None] | None:
    if aof is None:
        return None

    def persist(tokens: list[str], response: Any) -> None:
        if not tokens or response["type"] == "error":
            return

        if tokens[0] in MUTATING_COMMANDS:
            aof.append(tokens)

    return persist


def main() -> None:
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("Mini Redis server stopped")


if __name__ == "__main__":
    main()
