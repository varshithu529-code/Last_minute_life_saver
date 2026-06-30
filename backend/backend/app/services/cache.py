"""Redis cache wrapper with graceful degradation."""

import json
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """Cache layer for prioritization scores; falls back to no-op if Redis unavailable."""

    def __init__(self) -> None:
        self._client = None
        settings = get_settings()
        if settings.redis_enabled:
            try:
                import redis

                self._client = redis.from_url(settings.redis_url, decode_responses=True)
                self._client.ping()
                logger.info("Redis cache connected")
            except Exception as exc:
                logger.warning("Redis unavailable, caching disabled: %s", exc)
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def get(self, key: str) -> Any | None:
        if not self._client:
            return None
        try:
            raw = self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning("Cache get failed: %s", exc)
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if not self._client:
            return
        try:
            self._client.setex(key, ttl_seconds, json.dumps(value))
        except Exception as exc:
            logger.warning("Cache set failed: %s", exc)

    def delete(self, key: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(key)
        except Exception as exc:
            logger.warning("Cache delete failed: %s", exc)


cache_service = CacheService()
