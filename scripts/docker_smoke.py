"""Run Docker-based smoke checks against a disposable server container."""

from __future__ import annotations

import argparse
import subprocess
import time


def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, text=True, capture_output=True)


def cleanup(container_name: str, network_name: str) -> None:
    run_command(["docker", "rm", "-f", container_name], check=False)
    run_command(["docker", "network", "rm", network_name], check=False)


def wait_for_server(image: str, network_name: str, container_name: str, port: int) -> None:
    for _ in range(10):
        probe = run_command(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                network_name,
                "-e",
                f"REDIS_HOST={container_name}",
                "-e",
                f"REDIS_PORT={port}",
                image,
                "python",
                "scripts/smoke_test.py",
                "--timeout",
                "0.2",
            ],
            check=False,
        )
        if probe.returncode == 0:
            return
        time.sleep(0.5)

    raise RuntimeError("Server container did not become ready for smoke testing")


def run_smoke(image: str, network_name: str, container_name: str, port: int) -> None:
    cleanup(container_name, network_name)
    run_command(["docker", "network", "create", network_name])
    run_command(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "--network",
            network_name,
            "-e",
            "REDIS_HOST=0.0.0.0",
            "-e",
            f"REDIS_PORT={port}",
            image,
        ]
    )

    try:
        wait_for_server(image, network_name, container_name, port)
        run_command(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                network_name,
                "-e",
                f"REDIS_HOST={container_name}",
                "-e",
                f"REDIS_PORT={port}",
                "-e",
                "RUN_REDIS_SMOKE=1",
                image,
                "python",
                "-m",
                "pytest",
                "tests/smoke/test_server_smoke.py",
                "-q",
            ]
        )
    finally:
        cleanup(container_name, network_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--network", required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--port", type=int, default=6379)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run_smoke(args.image, args.network, args.container, args.port)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        if isinstance(exc, subprocess.CalledProcessError):
            if exc.stdout:
                print(exc.stdout, end="")
            if exc.stderr:
                print(exc.stderr, end="")
        else:
            print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
