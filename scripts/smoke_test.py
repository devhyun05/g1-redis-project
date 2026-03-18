"""Minimal TCP/RESP smoke test for a running Cycle 2 server."""

from __future__ import annotations

import argparse
import os
import socket
import sys


CRLF = b"\r\n"


def encode_command(tokens: list[str]) -> bytes:
    parts = [f"*{len(tokens)}\r\n".encode("utf-8")]

    for token in tokens:
        encoded = token.encode("utf-8")
        parts.append(f"${len(encoded)}\r\n".encode("utf-8"))
        parts.append(encoded + CRLF)

    return b"".join(parts)


def _read_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()

    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise RuntimeError("Socket closed before response was fully read")
        chunks.extend(chunk)

    return bytes(chunks)


def _read_line(sock: socket.socket) -> bytes:
    line = bytearray()

    while not line.endswith(CRLF):
        chunk = sock.recv(1)
        if not chunk:
            raise RuntimeError("Socket closed before line terminator was received")
        line.extend(chunk)

    return bytes(line)


def read_response(sock: socket.socket) -> bytes:
    prefix = _read_exact(sock, 1)
    line = _read_line(sock)

    if prefix in {b"+", b"-", b":"}:
        return prefix + line

    if prefix == b"$":
        if line == b"-1\r\n":
            return prefix + line

        payload_length = int(line[:-2].decode("utf-8"))
        payload = _read_exact(sock, payload_length + len(CRLF))
        return prefix + line + payload

    raise RuntimeError(f"Unsupported RESP response prefix: {prefix!r}")


def _send_payload(host: str, port: int, timeout: float, payload: bytes) -> bytes:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(payload)
        return read_response(sock)


def send_command(host: str, port: int, timeout: float, tokens: list[str]) -> bytes:
    return _send_payload(host, port, timeout, encode_command(tokens))


def send_raw_payload(host: str, port: int, timeout: float, payload: bytes) -> bytes:
    return _send_payload(host, port, timeout, payload)


def run_smoke_test(host: str, port: int, timeout: float = 1.0) -> None:
    assert send_command(host, port, timeout, ["PING"]) == b"+PONG\r\n"
    send_command(host, port, timeout, ["DEL", "smoke:key"])
    send_command(host, port, timeout, ["DEL", "smoke:counter"])
    assert send_command(host, port, timeout, ["SET", "smoke:key", "value"]) == b"+OK\r\n"
    assert send_command(host, port, timeout, ["GET", "smoke:key"]) == b"$5\r\nvalue\r\n"
    assert send_command(host, port, timeout, ["EXISTS", "smoke:key"]) == b":1\r\n"
    assert send_command(host, port, timeout, ["INCR", "smoke:counter"]) == b":1\r\n"
    assert send_command(host, port, timeout, ["INCR", "smoke:counter"]) == b":2\r\n"
    assert send_command(host, port, timeout, ["DECR", "smoke:counter"]) == b":1\r\n"
    assert send_command(host, port, timeout, ["GET", "smoke:counter"]) == b"$1\r\n1\r\n"
    assert send_command(host, port, timeout, ["DEL", "smoke:key"]) == b":1\r\n"
    assert send_command(host, port, timeout, ["EXISTS", "smoke:key"]) == b":0\r\n"
    assert send_command(host, port, timeout, ["GET", "smoke:key"]) == b"$-1\r\n"
    assert send_command(host, port, timeout, ["BOGUS"]) == b"-ERR unknown command 'BOGUS'\r\n"
    assert send_raw_payload(host, port, timeout, b"*1\r\n$bad\r\nPING\r\n") == b"-ERR protocol error\r\n"
    assert send_command(host, port, timeout, ["PING"]) == b"+PONG\r\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("REDIS_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("REDIS_PORT", "6379")))
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("SMOKE_TIMEOUT", "1.0")),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        run_smoke_test(args.host, args.port, args.timeout)
    except (AssertionError, OSError, RuntimeError, ValueError) as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        return 1

    print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
