"""In-memory, thread-safe transport — no external dependency.

Implements the Redis list+string subset over plain dicts/deques guarded by a
lock, with a condition variable so ``brpop`` can block until data arrives. Only
shares data within a single process, so it is only useful when the frame grabber
and input worker run as threads (see ``Game.start_frame_grabber`` /
``start_input_controller`` when ``transport.backend == in_process``).
"""

from __future__ import annotations

import fnmatch
import threading
from collections import deque

from serpent.transport.base import Transport


def _encode(value: bytes | str | int) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return str(value).encode("utf-8")


class InProcessTransport(Transport):
    def __init__(self):
        self._lists: dict[str, deque[bytes]] = {}
        self._values: dict[str, bytes] = {}
        self._condition = threading.Condition()

    def lpush(self, key, *values):
        with self._condition:
            target = self._lists.setdefault(key, deque())
            for value in values:
                target.appendleft(_encode(value))
            self._condition.notify_all()
            return len(target)

    def rpush(self, key, *values):
        with self._condition:
            target = self._lists.setdefault(key, deque())
            for value in values:
                target.append(_encode(value))
            self._condition.notify_all()
            return len(target)

    def lpop(self, key):
        with self._condition:
            target = self._lists.get(key)
            return target.popleft() if target else None

    def rpop(self, key):
        with self._condition:
            target = self._lists.get(key)
            return target.pop() if target else None

    def brpop(self, key, timeout=0):
        deadline = None if not timeout else (threading.TIMEOUT_MAX if timeout <= 0 else timeout)
        with self._condition:
            while not self._lists.get(key):
                if not self._condition.wait(timeout=deadline):
                    return None
            return (_encode(key), self._lists[key].pop())

    def lindex(self, key, index):
        with self._condition:
            target = self._lists.get(key)
            if not target:
                return None
            try:
                return target[index]
            except IndexError:
                return None

    def llen(self, key):
        with self._condition:
            target = self._lists.get(key)
            return len(target) if target else 0

    def ltrim(self, key, start, end):
        with self._condition:
            target = self._lists.get(key)
            if not target:
                return
            items = list(target)
            # Redis LTRIM: inclusive end; -1 means "to the last element".
            stop = len(items) if end == -1 else end + 1
            self._lists[key] = deque(items[start:stop])

    def get(self, key):
        with self._condition:
            return self._values.get(key)

    def set(self, key, value):
        with self._condition:
            self._values[key] = _encode(value)

    def delete(self, *keys):
        with self._condition:
            removed = 0
            for key in keys:
                removed += self._lists.pop(key, None) is not None
                removed += self._values.pop(key, None) is not None
            return removed

    def keys(self, pattern="*"):
        with self._condition:
            all_keys = set(self._lists) | set(self._values)
            return [_encode(k) for k in all_keys if fnmatch.fnmatch(k, pattern)]


__all__ = ["InProcessTransport"]
