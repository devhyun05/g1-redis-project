from src.server.traffic_stats import TrafficStats


def test_render_status_line_shows_zero_requests_before_traffic() -> None:
    stats = TrafficStats(aof_enabled=True)

    assert stats.render_status_line() == "[traffic] ░░░░░░░░ 0 req/s | hot key: - | aof: on"


def test_render_status_line_uses_recent_request_window_and_hot_key() -> None:
    stats = TrafficStats(aof_enabled=False)

    for _ in range(12):
        stats.record_request(["GET", "hits"])

    for _ in range(2):
        stats.record_request(["SET", "demo", "1"])

    assert (
        stats.render_status_line()
        == "[traffic] ██░░░░░░ 14 req/s | hot key: hits | aof: off"
    )

    assert stats.render_status_line() == "[traffic] ░░░░░░░░ 0 req/s | hot key: hits | aof: off"


def test_record_request_ignores_commands_without_keys_for_hot_key_tracking() -> None:
    stats = TrafficStats(aof_enabled=True)

    stats.record_request(["PING"])

    assert stats.render_status_line() == "[traffic] █░░░░░░░ 1 req/s | hot key: - | aof: on"
