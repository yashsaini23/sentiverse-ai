import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class MemoryManager:
    def __init__(self) -> None:
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = 86400

    @staticmethod
    def _session_key(session_id: str) -> str:
        safe_id = "".join(char for char in session_id if char.isalnum() or char in "-_")[:128]
        return f"session:{safe_id or 'anonymous_default_user'}"

    async def get_user_context(self, session_id: str) -> dict[str, Any]:
        data = await self.redis.get(self._session_key(session_id))
        if data:
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                parsed.setdefault("seen_items", [])
                parsed.setdefault("mood_history", [])
                return parsed
        return {"seen_items": [], "mood_history": []}

    async def update_user_context(self, session_id: str, new_mood: str, new_items: list[str]) -> None:
        context = await self.get_user_context(session_id)
        context["mood_history"] = (context.get("mood_history", []) + [new_mood])[-10:]
        context["seen_items"] = list(dict.fromkeys(context.get("seen_items", []) + new_items))
        await self.redis.setex(self._session_key(session_id), self.ttl, json.dumps(context))


memory_manager = MemoryManager()
