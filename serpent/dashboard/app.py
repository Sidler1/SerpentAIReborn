"""Serpent.AI dashboard — a local FastAPI web app.

Replaces the dead cefpython3/kivy/pony dashboard (which embedded a Chromium
browser pointed at an external, now-defunct site). This serves a self-contained
page showing the live analytics your agent emits: counts per event and a recent-
events feed, polled from a JSON API. A background thread drains analytics events
from the transport into a SQLite store (see analytics_consumer / store).

Run with ``serpent dashboard`` (or ``serpent.dashboard.app.run()``). Use the
``redis`` transport so a running agent and this app share the event stream.
"""

from __future__ import annotations

import asyncio
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from serpent.config import config
from serpent.dashboard.analytics_consumer import AnalyticsConsumer
from serpent.dashboard.store import DEFAULT_DB_PATH, EventStore


def _default_key() -> str:
    return config.get("analytics", {}).get("topic", "ANALYTICS_TOPIC")


_PAGE = """<!doctype html>
<html><head><title>Serpent.AI Dashboard</title>
<style>
  body {{ background:#23313f; color:#eee; font-family:sans-serif; margin:1.5rem; }}
  h2 {{ color:#7fb; }}
  .summary {{ display:flex; flex-wrap:wrap; gap:1rem; margin-bottom:1rem; }}
  .metric {{ background:#1b2630; padding:.75rem 1rem; border-radius:6px; min-width:8rem; }}
  .metric .n {{ font-size:1.6rem; color:#7fb; }}
  table {{ border-collapse:collapse; width:100%; }}
  th, td {{ text-align:left; padding:.35rem .6rem; border-bottom:1px solid #34465a; }}
  td, th {{ font-size:.9rem; }}
  th {{ color:#7fb; }}
</style></head>
<body>
  <h2>Serpent.AI Dashboard <small style="color:#789">({key})</small></h2>
  <div id="summary" class="summary"></div>
  <h3>Recent events</h3>
  <table><thead><tr><th>timestamp</th><th>event</th><th>data</th></tr></thead>
  <tbody id="events"></tbody></table>
  <script>
    function render({{summary, events}}) {{
      document.getElementById("summary").innerHTML = Object.entries(summary)
        .map(([k, n]) => `<div class="metric"><div>${{k}}</div><div class="n">${{n}}</div></div>`)
        .join("");
      document.getElementById("events").innerHTML = events
        .map(e => `<tr><td>${{e.timestamp ?? ""}}</td><td>${{e.event_key ?? ""}}</td>`
                + `<td>${{JSON.stringify(e.data)}}</td></tr>`)
        .join("");
    }}
    async function poll() {{
      const [summary, events] = await Promise.all([
        fetch("/api/summary").then(r => r.json()),
        fetch("/api/events?limit=100").then(r => r.json()),
      ]);
      render({{summary, events}});
    }}
    // Prefer the live WebSocket feed; fall back to polling if it drops.
    function connect() {{
      const ws = new WebSocket(`ws://${{location.host}}/ws`);
      ws.onmessage = (m) => render(JSON.parse(m.data));
      ws.onclose = () => {{ poll(); setTimeout(connect, 2000); }};
      ws.onerror = () => ws.close();
    }}
    connect();
  </script>
</body></html>"""


def create_app(project_key=None, db_path=None, start_consumer=False) -> FastAPI:
    app = FastAPI(title="Serpent.AI Dashboard")

    store = EventStore(db_path or DEFAULT_DB_PATH)
    key = project_key or _default_key()

    app.state.store = store

    if start_consumer:
        consumer = AnalyticsConsumer(store, key)
        threading.Thread(target=consumer.run, daemon=True).start()

    @app.get("/api/events")
    def events(limit: int = 100):
        return store.recent_events(limit)

    @app.get("/api/summary")
    def summary():
        return store.event_counts()

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _PAGE.format(key=key)

    @app.websocket("/ws")
    async def ws(websocket: WebSocket, interval: float = 1.0):
        await websocket.accept()
        try:
            while True:
                await websocket.send_json(
                    {"summary": store.event_counts(), "events": store.recent_events(100)}
                )
                await asyncio.sleep(interval)
        except WebSocketDisconnect:
            return

    return app


def run(host: str = "127.0.0.1", port: int = 8500, project_key=None, db_path=None) -> None:
    import uvicorn

    uvicorn.run(
        create_app(project_key=project_key, db_path=db_path, start_consumer=True),
        host=host,
        port=port,
    )


if __name__ == "__main__":
    run()
