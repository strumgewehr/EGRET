"""
Redis cache for API responses. Reduces DB load and improves latency.
"""
import json
from typing import Any, Optional
import redis
from app.config import get_settings

_settings = get_settings()
_client: Optional[redis.Redis] = None
CACHE_TTL = 300  # 5 minutes for dashboard/list responses


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(_settings.redis_url, decode_responses=True)
    return _client


def cache_get(key: str) -> Optional[Any]:
    if not _settings.redis_url or "localhost" in _settings.redis_url:
        return None
    try:
        r = get_redis()
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = CACHE_TTL) -> None:
    if not _settings.redis_url or "localhost" in _settings.redis_url:
        return
    try:
        r = get_redis()
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_delete_pattern(pattern: str) -> None:
    try:
        r = get_redis()
        for k in r.scan_iter(match=pattern):
            r.delete(k)
    except Exception:
        pass
