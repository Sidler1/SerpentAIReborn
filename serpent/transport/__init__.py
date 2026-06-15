"""Pluggable transport for Serpent's frame / input / analytics bus.

The bus was historically a hard-wired Redis dependency. It is now abstracted
behind :class:`~serpent.transport.base.Transport`, a minimal subset of Redis
list+string semantics, with two backends:

- :class:`~serpent.transport.redis_transport.RedisTransport` (default) — the
  original behaviour; works across separate OS processes (the frame grabber and
  input worker are spawned as subprocesses).
- :class:`~serpent.transport.in_process_transport.InProcessTransport` — an
  in-memory, thread-safe store with no external dependency. Only meaningful when
  producers/consumers share a process (the grabber/worker run as threads).

Selected via the ``transport.backend`` config key (``redis`` | ``in_process``).
:func:`get_transport` returns a process-wide singleton.
"""

from __future__ import annotations

from serpent.config import config
from serpent.transport.base import Transport

_TRANSPORT: Transport | None = None


def build_transport(backend: str | None = None) -> Transport:
    """Construct a fresh transport for the given backend (defaults to config)."""
    if backend is None:
        backend = config.get("transport", {}).get("backend", "redis")

    if backend == "redis":
        from serpent.transport.redis_transport import RedisTransport

        return RedisTransport(**config["redis"])
    elif backend == "in_process":
        from serpent.transport.in_process_transport import InProcessTransport

        return InProcessTransport()

    raise ValueError(f"Unknown transport backend: '{backend}'")


def get_transport() -> Transport:
    """Return the process-wide transport singleton (built from config)."""
    global _TRANSPORT

    if _TRANSPORT is None:
        _TRANSPORT = build_transport()

    return _TRANSPORT


__all__ = ["Transport", "build_transport", "get_transport"]
