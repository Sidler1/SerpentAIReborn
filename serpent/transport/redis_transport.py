"""Redis-backed transport — a thin pass-through to redis-py (the default)."""

from __future__ import annotations

from redis import StrictRedis

from serpent.transport.base import Transport


class RedisTransport(Transport):
    def __init__(self, **redis_kwargs):
        self._client = StrictRedis(**redis_kwargs)

    @property
    def client(self) -> StrictRedis:
        return self._client

    def lpush(self, key, *values):
        return self._client.lpush(key, *values)

    def rpush(self, key, *values):
        return self._client.rpush(key, *values)

    def lpop(self, key):
        return self._client.lpop(key)

    def rpop(self, key):
        return self._client.rpop(key)

    def brpop(self, key, timeout=0):
        return self._client.brpop(key, timeout=timeout)

    def lindex(self, key, index):
        return self._client.lindex(key, index)

    def llen(self, key):
        return self._client.llen(key)

    def ltrim(self, key, start, end):
        self._client.ltrim(key, start, end)

    def get(self, key):
        return self._client.get(key)

    def set(self, key, value):
        self._client.set(key, value)

    def delete(self, *keys):
        return self._client.delete(*keys)

    def keys(self, pattern="*"):
        return self._client.keys(pattern)


__all__ = ["RedisTransport"]
