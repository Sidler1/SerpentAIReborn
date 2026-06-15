"""Phase H: modern dashboard (sqlite store + analytics consumer + FastAPI app)."""

import json

import pytest
from fastapi.testclient import TestClient

import serpent.transport as transport_module
from serpent.dashboard.analytics_consumer import AnalyticsConsumer
from serpent.dashboard.app import create_app
from serpent.dashboard.store import EventStore
from serpent.transport.in_process_transport import InProcessTransport


@pytest.fixture
def in_process_transport(monkeypatch):
    transport = InProcessTransport()
    monkeypatch.setattr(transport_module, "_TRANSPORT", transport)
    return transport


def _event(event_key, value):
    return {
        "project_key": "PROJ",
        "event_key": event_key,
        "data": {"value": value},
        "timestamp": "2026-06-15T00:00:00",
        "is_persistable": True,
    }


def test_event_store_roundtrip(tmp_path):
    store = EventStore(tmp_path / "a.sqlite")

    store.record_event(_event("REWARD", 1))
    store.record_event(_event("REWARD", 2))
    store.record_event(_event("DEATH", 0))

    recent = store.recent_events()
    assert [e["event_key"] for e in recent] == ["DEATH", "REWARD", "REWARD"]  # newest first
    assert recent[-1]["data"] == {"value": 1}
    assert store.event_counts() == {"REWARD": 2, "DEATH": 1}

    store.clear()
    assert store.recent_events() == []


def test_analytics_consumer_persists_from_transport(tmp_path, in_process_transport):
    store = EventStore(tmp_path / "a.sqlite")
    consumer = AnalyticsConsumer(store, key="PROJ")

    assert consumer.consume_once() is False  # nothing queued yet

    in_process_transport.lpush("SERPENT:PROJ:EVENTS", json.dumps(_event("REWARD", 5)))
    assert consumer.consume_once() is True

    events = store.recent_events()
    assert len(events) == 1
    assert events[0]["event_key"] == "REWARD"
    assert events[0]["data"] == {"value": 5}


def test_dashboard_api_and_page(tmp_path, in_process_transport):
    app = create_app(project_key="PROJ", db_path=tmp_path / "a.sqlite", start_consumer=False)
    app.state.store.record_event(_event("REWARD", 9))

    client = TestClient(app)

    events = client.get("/api/events").json()
    assert events[0]["event_key"] == "REWARD"

    assert client.get("/api/summary").json() == {"REWARD": 1}

    page = client.get("/")
    assert page.status_code == 200
    assert "Serpent.AI Dashboard" in page.text
