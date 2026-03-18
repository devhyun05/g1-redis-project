from pathlib import Path

from src.main import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_READ_BUFFER_SIZE,
    ENV_AOF_ENABLED_KEY,
    ENV_AOF_PATH_KEY,
    ENV_HOST_KEY,
    ENV_PORT_KEY,
    ENV_READ_BUFFER_SIZE_KEY,
    load_dotenv,
    load_server_config,
)


def test_load_dotenv_sets_missing_env_values_from_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n".join(
            [
                "# comment",
                f"{ENV_HOST_KEY}=10.0.0.5",
                f"{ENV_PORT_KEY}=6380",
                f"{ENV_READ_BUFFER_SIZE_KEY}=8192",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv(ENV_HOST_KEY, raising=False)
    monkeypatch.delenv(ENV_PORT_KEY, raising=False)
    monkeypatch.delenv(ENV_READ_BUFFER_SIZE_KEY, raising=False)
    monkeypatch.delenv(ENV_AOF_ENABLED_KEY, raising=False)
    monkeypatch.delenv(ENV_AOF_PATH_KEY, raising=False)

    load_dotenv(dotenv_path)

    assert load_server_config() == ("10.0.0.5", 6380, 8192, False, Path("data/appendonly.aof"))


def test_load_dotenv_does_not_override_existing_environment(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(f"{ENV_HOST_KEY}=10.0.0.5\n", encoding="utf-8")
    monkeypatch.setenv(ENV_HOST_KEY, "127.0.0.9")

    load_dotenv(dotenv_path)

    assert load_server_config()[0] == "127.0.0.9"


def test_load_server_config_uses_defaults_when_env_is_missing(monkeypatch) -> None:
    monkeypatch.delenv(ENV_HOST_KEY, raising=False)
    monkeypatch.delenv(ENV_PORT_KEY, raising=False)
    monkeypatch.delenv(ENV_READ_BUFFER_SIZE_KEY, raising=False)
    monkeypatch.delenv(ENV_AOF_ENABLED_KEY, raising=False)
    monkeypatch.delenv(ENV_AOF_PATH_KEY, raising=False)

    assert load_server_config() == (
        DEFAULT_HOST,
        DEFAULT_PORT,
        DEFAULT_READ_BUFFER_SIZE,
        False,
        Path("data/appendonly.aof"),
    )


def test_load_server_config_falls_back_for_invalid_integers(monkeypatch) -> None:
    monkeypatch.setenv(ENV_HOST_KEY, "127.0.0.2")
    monkeypatch.setenv(ENV_PORT_KEY, "not-a-number")
    monkeypatch.setenv(ENV_READ_BUFFER_SIZE_KEY, "bad")
    monkeypatch.delenv(ENV_AOF_ENABLED_KEY, raising=False)
    monkeypatch.delenv(ENV_AOF_PATH_KEY, raising=False)

    assert load_server_config() == (
        "127.0.0.2",
        DEFAULT_PORT,
        DEFAULT_READ_BUFFER_SIZE,
        False,
        Path("data/appendonly.aof"),
    )
