import hashlib
import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.memory import memory_manager

logger = logging.getLogger(__name__)


class LLMExplainer:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT_SECONDS) if settings.OPENAI_API_KEY else None
        self.model = settings.OPENAI_MODEL
        self.cache_ttl = 7 * 24 * 60 * 60

    @staticmethod
    def _generate_cache_key(mood: str, media_id: str) -> str:
        mood_hash = hashlib.sha256(mood.strip().lower().encode("utf-8")).hexdigest()
        return f"llm_cache:{media_id}:{mood_hash}"

    @staticmethod
    def _fallback(user_mood: str, media_meta: dict) -> str:
        title = str(media_meta.get("title", "this recommendation"))
        themes = str(media_meta.get("themes", "its themes"))
        medium = str(media_meta.get("medium", "title"))
        return f"{title} explores {themes}, which may resonate with how you're feeling about '{user_mood}'. This {medium.lower()} offers a way to reflect on that mood at your own pace."

    async def generate_explanation(self, user_mood: str, media_meta: dict, media_id: str) -> str:
        cache_key = self._generate_cache_key(user_mood, media_id)
        try:
            cached = await memory_manager.redis.get(cache_key)
            if cached:
                return cached
        except Exception:
            logger.warning("Redis cache read failed; continuing without cache.", exc_info=True)

        if self.client is None:
            return self._fallback(user_mood, media_meta)

        title = media_meta.get("title", "this title")
        medium = media_meta.get("medium", "item")
        themes = media_meta.get("themes", "complex themes")
        tone = media_meta.get("tone", "nuanced")
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are SentiVerse, an empathetic entertainment curator. Explain why a piece of media may fit the user's stated mood. Avoid claiming to know the user's mental state. Write exactly two concise sentences."},
                    {"role": "user", "content": f"User mood: {user_mood!r}\nRecommended {medium}: {title!r}\nThemes: {themes}\nTone: {tone}\nWrite the explanation."},
                ],
                max_tokens=120,
                temperature=0.7,
            )
            explanation = response.choices[0].message.content
            if not explanation:
                return self._fallback(user_mood, media_meta)
            explanation = explanation.strip()
            try:
                await memory_manager.redis.setex(cache_key, self.cache_ttl, explanation)
            except Exception:
                logger.warning("Redis cache write failed.", exc_info=True)
            return explanation
        except Exception:
            logger.exception("LLM explanation generation failed.")
            return self._fallback(user_mood, media_meta)


llm_explainer = LLMExplainer()
