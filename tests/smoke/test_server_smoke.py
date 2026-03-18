import os

import pytest

from scripts.smoke_test import run_smoke_test


if os.getenv("RUN_REDIS_SMOKE") != "1":
    pytest.skip(
        "Smoke test requires RUN_REDIS_SMOKE=1 and a running TCP server",
        allow_module_level=True,
    )


def test_server_round_trip_smoke() -> None:
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    port = int(os.getenv("REDIS_PORT", "6379"))
    timeout = float(os.getenv("SMOKE_TIMEOUT", "1.0"))

    run_smoke_test(host, port, timeout)
