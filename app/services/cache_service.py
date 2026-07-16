import copy
import time
from threading import Lock
from typing import Any

from app.core.config import CACHE_TTL_SECONDS


class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, tuple[float, Any]] = {}
        self._hits = 0
        self._misses = 0
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        if self.ttl_seconds <= 0:
            with self._lock:
                self._misses += 1
            return None

        now = time.time()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                self._misses += 1
                return None

            expires_at, value = item
            if expires_at <= now:
                self._items.pop(key, None)
                self._misses += 1
                return None

            self._hits += 1
            return copy.deepcopy(value)

    def set(self, key: str, value: Any) -> None:
        if self.ttl_seconds <= 0:
            return

        expires_at = time.time() + self.ttl_seconds
        with self._lock:
            self._items[key] = (expires_at, copy.deepcopy(value))

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> dict:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total else 0.0
            return {
                "enabled": self.ttl_seconds > 0,
                "ttl_seconds": self.ttl_seconds,
                "entries": len(self._items),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
            }


wallet_pipeline_cache = TTLCache(ttl_seconds=CACHE_TTL_SECONDS)
