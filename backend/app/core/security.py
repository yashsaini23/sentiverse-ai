import time
from fastapi import Request, HTTPException
from app.core.memory import memory_manager

class RateLimiter:
    def __init__(self, requests_per_minute: int = 20):
        self.rpm = requests_per_minute

    async def check_rate_limit(self, request: Request):
        """
        Uses Redis to track request counts per IP.
        Blocks the request with a 429 status code if the threshold is exceeded.
        """
        # Get client IP, respecting Nginx reverse proxies
        client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0]
        
        # We use a sliding window bucket based on the current minute
        current_minute = int(time.time() / 60)
        redis_key = f"rate_limit:{client_ip}:{current_minute}"

        try:
            # Atomic increment
            request_count = await memory_manager.redis.incr(redis_key)
            
            # Set expiry for cleanup if it's a new key
            if request_count == 1:
                await memory_manager.redis.expire(redis_key, 60)

            if request_count > self.rpm:
                raise HTTPException(
                    status_code=429, 
                    detail="Rate limit exceeded. Please wait a moment before searching your feelings again."
                )
        except HTTPException:
            raise
        except Exception as e:
            # Fail open if Redis drops connection so the app doesn't go offline
            print(f"Rate limiter bypassed due to Redis error: {str(e)}")

rate_limiter = RateLimiter(requests_per_minute=15)