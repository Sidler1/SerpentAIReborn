"""The Transport interface — a minimal subset of Redis list + string commands.

Method names and semantics mirror redis-py so migrating call sites is mechanical
(``redis_client.lpush`` -> ``transport.lpush``). Values are bytes on the way out,
matching redis-py's default (``decode_responses=False``); callers ``.decode()``
as needed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Transport(ABC):
    # List operations
    @abstractmethod
    def lpush(self, key: str, *values: bytes | str) -> int: ...

    @abstractmethod
    def rpush(self, key: str, *values: bytes | str) -> int: ...

    @abstractmethod
    def lpop(self, key: str) -> bytes | None: ...

    @abstractmethod
    def rpop(self, key: str) -> bytes | None: ...

    @abstractmethod
    def brpop(self, key: str, timeout: float = 0) -> tuple[bytes, bytes] | None: ...

    @abstractmethod
    def lindex(self, key: str, index: int) -> bytes | None: ...

    @abstractmethod
    def llen(self, key: str) -> int: ...

    @abstractmethod
    def ltrim(self, key: str, start: int, end: int) -> None: ...

    # String / key operations
    @abstractmethod
    def get(self, key: str) -> bytes | None: ...

    @abstractmethod
    def set(self, key: str, value: bytes | str) -> None: ...

    @abstractmethod
    def delete(self, *keys: str) -> int: ...

    @abstractmethod
    def keys(self, pattern: str = "*") -> list[bytes]: ...


__all__ = ["Transport"]
