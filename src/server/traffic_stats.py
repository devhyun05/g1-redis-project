from __future__ import annotations

import math


KEYED_COMMANDS = {"SET", "GET", "DEL", "EXISTS", "INCR", "DECR"}
BAR_WIDTH = 8
REQUESTS_PER_BLOCK = 10


class TrafficStats:
    def __init__(self, aof_enabled: bool) -> None:
        self._aof_enabled = aof_enabled
        self._window_requests = 0
        self._key_counts: dict[str, int] = {}

    def record_request(self, tokens: list[str]) -> None:
        self._window_requests += 1

        key = _extract_key(tokens)
        if key is None:
            return

        self._key_counts[key] = self._key_counts.get(key, 0) + 1

    def render_status_line(self) -> str:
        requests_per_second = self._window_requests
        self._window_requests = 0

        bar = _render_bar(requests_per_second)
        hot_key = _find_hot_key(self._key_counts)
        aof_status = "on" if self._aof_enabled else "off"
        return (
            f"[traffic] {bar} {requests_per_second} req/s"
            f" | hot key: {hot_key} | aof: {aof_status}"
        )


def _extract_key(tokens: list[str]) -> str | None:
    if len(tokens) < 2 or tokens[0] not in KEYED_COMMANDS:
        return None

    return tokens[1]


def _find_hot_key(key_counts: dict[str, int]) -> str:
    if not key_counts:
        return "-"

    return min(key_counts, key=lambda key: (-key_counts[key], key))


def _render_bar(requests_per_second: int) -> str:
    if requests_per_second <= 0:
        filled_blocks = 0
    else:
        filled_blocks = min(
            BAR_WIDTH,
            max(1, math.ceil(requests_per_second / REQUESTS_PER_BLOCK)),
        )

    return ("█" * filled_blocks) + ("░" * (BAR_WIDTH - filled_blocks))
