import redis.asyncio as redis
import json
import os
from typing import List, Dict

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class MemoryManager:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
        self.ttl = 86400 # 24-hour memory retention

    async def get_user_context(self, session_id: str) -> Dict:
        """Retrieves previously recommended items and past moods."""
        data = await self.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return {"seen_items": [], "mood_history": []}

    async def update_user_context(self, session_id: str, new_mood: str, new_items: List[str]):
        """Appends new recommendations and mood queries to the user's session."""
        context = await self.get_user_context(session_id)
        
        # Prevent memory bloat
        context["mood_history"] = (context["mood_history"] + [new_mood])[-10:]
        context["seen_items"] = list(set(context["seen_items"] + new_items))

        await self.redis.setex(
            f"session:{session_id}", 
            self.ttl, 
            json.dumps(context)
        )

memory_manager = MemoryManager()