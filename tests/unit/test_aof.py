from pathlib import Path

import pytest

from src.commands.handler import handle_command
from src.storage.aof import AppendOnlyFile
from src.storage.store import Store


def test_aof_replays_mutating_commands(tmp_path: Path) -> None:
    aof = AppendOnlyFile(tmp_path / "appendonly.aof")
    aof.append(["SET", "user", "alice"])
    aof.append(["INCR", "counter"])
    aof.append(["DECR", "counter"])
    aof.append(["DEL", "user"])

    recovered_store = Store()
    aof.replay(recovered_store, handle_command)

    assert recovered_store.get("user") is None
    assert recovered_store.get("counter") == "0"


def test_aof_ignores_missing_file_on_replay(tmp_path: Path) -> None:
    aof = AppendOnlyFile(tmp_path / "missing.aof")
    store = Store()

    aof.replay(store, handle_command)

    assert store.get("missing") is None


def test_aof_replay_raises_for_incomplete_frame(tmp_path: Path) -> None:
    path = tmp_path / "appendonly.aof"
    path.write_bytes(b"*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n")
    aof = AppendOnlyFile(path)

    with pytest.raises(ValueError, match="incomplete RESP frame"):
        aof.replay(Store(), handle_command)
