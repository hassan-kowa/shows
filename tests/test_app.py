import json
import logging

import logging_config


def test_index_returns_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_search_returns_matching_shows(client):
    response = client.get("/search?q=office")
    assert response.status_code == 200
    titles = [show["title"] for show in response.get_json()]
    assert titles == ["The Office", "The Office (UK)"]


def test_search_without_query_returns_empty_list(client):
    response = client.get("/search")
    assert response.status_code == 200
    assert response.get_json() == []


def test_search_with_no_match_returns_empty_list(client):
    response = client.get("/search?q=zzzzqq")
    assert response.status_code == 200
    assert response.get_json() == []


def test_search_failure_returns_500_and_logs_error(client, app_module, monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise RuntimeError("simulated database failure")

    monkeypatch.setattr(app_module.db, "execute", boom)

    with caplog.at_level(logging.ERROR):
        response = client.get("/search?q=office")

    assert response.status_code == 500
    assert response.get_json() == []

    events = [r.msg for r in caplog.records if isinstance(r.msg, dict)]
    failed = [e for e in events if e.get("event") == "search_failed"]
    assert failed, "expected a search_failed log event"
    assert failed[0]["query"] == "office"
    assert failed[0]["exc_info"]


def test_log_file_contains_json_lines(client):
    client.get("/")
    lines = logging_config.LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    assert lines
    last = json.loads(lines[-1])
    assert last["event"] == "request"
    assert last["path"] == "/"
    assert last["status"] == 200
    assert last["level"] == "info"
