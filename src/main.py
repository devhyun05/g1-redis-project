from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable

from src.commands.handler import handle_command
from src.protocol.parser import parse_request
from src.protocol.writer import encode_response
from src.server.tcp_server import TcpServer
from src.server.traffic_stats import TrafficStats
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
ENV_LOG_LEVEL_KEY = "LOG_LEVEL"
ENV_LOG_REQUESTS_KEY = "LOG_REQUESTS"
DEFAULT_LOG_LEVEL = "INFO"

BANNER = r"""
                mini -

██████╗ ███████╗██████╗ ██╗███████╗
██╔══██╗██╔════╝██╔══██╗██║██╔════╝
██████╔╝█████╗  ██║  ██║██║███████╗
██╔══██╗██╔══╝  ██║  ██║██║╚════██║
██║  ██║███████╗██████╔╝██║███████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝╚══════╝

       small name, big latency saving -
""".strip("\n")

INFO_CARD = """
+----------------------------------+
|  REDIS MINI SERVER               |
|  Mode        : demo              |
|  Protocol    : TCP / RESP        |
|  Storage     : In-memory + AOF   |
|  Commands    : PING SET GET INCR |
+----------------------------------+
""".strip("\n")


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
    configure_logging()

    host, port, read_buffer_size, aof_enabled, aof_path = load_server_config()
    log_requests = _load_bool_env(ENV_LOG_REQUESTS_KEY, default=True)
    store = Store()
    aof = AppendOnlyFile(aof_path) if aof_enabled else None
    traffic_stats = TrafficStats(aof_enabled=aof_enabled)

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
        record_request=traffic_stats.record_request,
        read_size=read_buffer_size,
        log_requests=log_requests,
    )

    await server.start()
    logging.getLogger("mini_redis.main").info(
        json.dumps(
            {
                "event": "server_started",
                "host": host,
                "port": port,
                "read_buffer_size": read_buffer_size,
                "aof_enabled": aof_enabled,
                "log_requests": log_requests,
            },
            separators=(",", ":"),
        )
    )
    print(BANNER)
    print(INFO_CARD)
    print(f"Mini Redis server listening on {host}:{port}")
    traffic_task = asyncio.create_task(_display_traffic(traffic_stats))
    try:
        await server.serve_forever()
    finally:
        traffic_task.cancel()
        try:
            await traffic_task
        except asyncio.CancelledError:
            pass
        await server.shutdown()


def configure_logging() -> None:
    raw_level = os.getenv(ENV_LOG_LEVEL_KEY, DEFAULT_LOG_LEVEL).strip().upper()
    level_name = raw_level or DEFAULT_LOG_LEVEL
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(message)s")


def _persist_command(aof: AppendOnlyFile | None) -> Callable[[list[str], Any], None] | None:
    if aof is None:
        return None

    def persist(tokens: list[str], response: Any) -> None:
        if not tokens or response["type"] == "error":
            return

        if tokens[0] in MUTATING_COMMANDS:
            aof.append(tokens)

    return persist


async def _display_traffic(traffic_stats: TrafficStats) -> None:
    previous_length = 0

    try:
        while True:
            line = traffic_stats.render_status_line()
            previous_length = _write_status_line(line, previous_length)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        if previous_length > 0:
            sys.stdout.write("\n")
            sys.stdout.flush()
        raise


def _write_status_line(line: str, previous_length: int) -> int:
    padded_line = line
    if len(line) < previous_length:
        padded_line += " " * (previous_length - len(line))

    sys.stdout.write(f"\r{padded_line}")
    sys.stdout.flush()
    return len(line)


def main() -> None:
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("Mini Redis server stopped")


if __name__ == "__main__":
    main()
