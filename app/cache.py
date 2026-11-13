import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import get_settings

logger = logging.getLogger(__name__)
redis_client = Redis.from_url(get_settings().redis_url, decode_responses=True)


def cache_key(question: str) -> str:
    return f"qa:answer:{question.strip().casefold()}"


async def get_cached_answer(question: str) -> str | None:
    try:
        return await redis_client.get(cache_key(question))
    except (RedisError, OSError):
        logger.warning("Redis read failed; continuing without cache", exc_info=True)
        return None


async def cache_answer(question: str, answer: str) -> None:
    try:
        await redis_client.set(cache_key(question), answer, ex=get_settings().cache_ttl_seconds)
    except (RedisError, OSError):
        logger.warning("Redis write failed; answer was still persisted", exc_info=True)


async def clear_cache() -> None:
    try:
        keys = [key async for key in redis_client.scan_iter(match="qa:answer:*")]
        if keys:
            await redis_client.delete(*keys)
    except (RedisError, OSError):
        logger.warning("Redis cache clear failed", exc_info=True)


async def redis_is_healthy() -> bool:
    try:
        return bool(await redis_client.ping())
    except (RedisError, OSError):
        return False
