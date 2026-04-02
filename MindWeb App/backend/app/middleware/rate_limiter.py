import time
import uuid

import redis as redis_sync
from fastapi import HTTPException, Request, status

from app.config import settings

_redis = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)


def rate_limit(max_calls: int, window_seconds: int):
    """
    Sliding-window rate limiter decorator factory.
    Usage: @rate_limit(max_calls=10, window_seconds=60)
    """
    def decorator(func):
        import functools

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request") or next(
                (a for a in args if isinstance(a, Request)), None
            )
            key_prefix = "rl"

            if request is not None:
                identifier = request.client.host if request.client else "unknown"
            else:
                identifier = "unknown"

            key = f"{key_prefix}:{identifier}:{func.__name__}"
            now = int(time.time())
            window_start = now - window_seconds

            pipe = _redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds)
            results = pipe.execute()

            call_count = results[2]
            if call_count > max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {max_calls} requests per {window_seconds}s.",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_suggestion_count_today(user_id: uuid.UUID) -> int:
    key = f"suggestions:{user_id}:{_today_key()}"
    count = _redis.get(key)
    return int(count) if count else 0


def increment_suggestion_count(user_id: uuid.UUID) -> int:
    key = f"suggestions:{user_id}:{_today_key()}"
    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)  # TTL 24h
    result = pipe.execute()
    return result[0]


def _today_key() -> str:
    from datetime import date
    return date.today().isoformat()


def cache_suggestions(user_id: uuid.UUID, data: str) -> None:
    key = f"suggestions_cache:{user_id}"
    _redis.setex(key, 3600, data)  # TTL 1h


def get_cached_suggestions(user_id: uuid.UUID) -> str | None:
    return _redis.get(f"suggestions_cache:{user_id}")
