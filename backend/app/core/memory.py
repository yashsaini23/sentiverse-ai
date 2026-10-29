import json
import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self) -> None:
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = 86400

    async def get_user_context(self, session_id: str) -> dict:
        data = await self.redis.get(f"session:{session_id}")
        if not data:
            return {"seen_items": [], "mood_history": []}
        try:
            context = json.loads(data)
        except json.JSONDecodeError:
            logger.warning("Invalid session context; starting fresh.")
            return {"seen_items": [], "mood_history": []}
        if not isinstance(context, dict):
            return {"seen_items": [], "mood_history": []}
        context.setdefault("seen_items", [])
        context.setdefault("mood_history", [])
        return context

    async def update_user_context(self, session_id: str, new_mood: str, new_items: list[str]) -> None:
        context = await self.get_user_context(session_id)
        context["mood_history"] = (context["mood_history"] + [new_mood])[-10:]
        context["seen_items"] = list(dict.fromkeys(context["seen_items"] + new_items))
        await self.redis.setex(f"session:{session_id}", self.ttl, json.dumps(context))


memory_manager = MemoryManager()
