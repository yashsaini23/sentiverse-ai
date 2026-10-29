import logging
import time

from fastapi import HTTPException, Request

from app.core.memory import memory_manager

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, requests_per_minute: int = 20) -> None:
        self.rpm = requests_per_minute

    async def check_rate_limit(self, request: Request) -> None:
        # Do not trust X-Forwarded-For unless a trusted proxy is explicitly configured.
        client_ip = request.client.host if request.client else "unknown"
        current_minute = int(time.time() // 60)
        redis_key = f"rate_limit:{client_ip}:{current_minute}"
        try:
            request_count = await memory_manager.redis.incr(redis_key)
            if request_count == 1:
                await memory_manager.redis.expire(redis_key, 60)
            if request_count > self.rpm:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before trying again.")
        except HTTPException:
            raise
        except Exception:
            logger.warning("Rate limiter bypassed because Redis is unavailable", exc_info=True)


rate_limiter = RateLimiter(requests_per_minute=15)
