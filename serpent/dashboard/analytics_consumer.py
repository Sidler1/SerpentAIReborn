"""Analytics consumer — drains agent analytics events into the EventStore.

Replaces the WAMP ``analytics_component`` removed in Phase D. ``AnalyticsClient``
``lpush``-es JSON events onto ``SERPENT:<key>:EVENTS``; this consumer ``brpop``-s
them (FIFO) and persists them so the dashboard can read them back. Runs in a
background thread inside the dashboard app, or standalone.
"""

from __future__ import annotations

import json

from serpent.dashboard.store import EventStore
from serpent.transport import get_transport


class AnalyticsConsumer:
    def __init__(self, store: EventStore, key: str):
        self.store = store
        self.transport = get_transport()
        self.list_key = f"SERPENT:{key}:EVENTS"

    def consume_once(self) -> bool:
        """Persist one queued event if present (non-blocking). Returns whether one was consumed."""
        payload = self.transport.rpop(self.list_key)
        if payload is None:
            return False

        self.store.record_event(json.loads(payload.decode("utf-8")))
        return True

    def run(self) -> None:
        while True:
            result = self.transport.brpop(self.list_key, timeout=1)
            if result is None:
                continue

            _, payload = result
            self.store.record_event(json.loads(payload.decode("utf-8")))
