import hashlib
import logging
import os

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.memory import memory_manager

logger = logging.getLogger(__name__)


class LLMExplainer:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", settings.OPENAI_MODEL)
        self.cache_ttl = 604800

    @staticmethod
    def _generate_cache_key(mood: str, media_id: str) -> str:
        mood_hash = hashlib.sha256(mood.strip().lower().encode("utf-8")).hexdigest()
        return f"llm_cache:{media_id}:{mood_hash}"

    async def generate_explanation(self, user_mood: str, media_meta: dict, media_id: str) -> str:
        cache_key = self._generate_cache_key(user_mood, media_id)
        try:
            cached = await memory_manager.redis.get(cache_key)
            if cached:
                return cached
        except Exception:
            logger.warning("Redis explanation-cache read failed", exc_info=True)

        title = str(media_meta.get("title", "this title"))
        medium = str(media_meta.get("medium", "item"))
        themes = str(media_meta.get("themes", "complex themes"))
        tone = str(media_meta.get("tone", "nuanced"))
        fallback = (
            f"The themes of {themes} in {title} may resonate with how you're feeling. "
            "Take what feels helpful and leave the rest."
        )

        if self.client is None:
            logger.info("OPENAI_API_KEY is not configured; using the local explanation fallback.")
            return fallback

        system_prompt = (
            "You are SentiVerse, an empathetic AI entertainment curator. "
            "Explain why this media may fit the user's stated mood. "
            "Use exactly two concise, natural sentences; validate feelings without diagnosing, "
            "making promises, or claiming the media will treat a condition."
        )
        user_prompt = (
            f"User mood: {user_mood!r}\nRecommended {medium}: {title!r}\n"
            f"Themes: {themes}\nTone: {tone}\nWrite the explanation."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=100,
                temperature=0.7,
            )
            explanation = (response.choices[0].message.content or "").strip()
            if not explanation:
                return fallback
            try:
                await memory_manager.redis.setex(cache_key, self.cache_ttl, explanation)
            except Exception:
                logger.warning("Redis explanation-cache write failed", exc_info=True)
            return explanation
        except Exception:
            logger.exception("LLM explanation generation failed")
            return fallback


llm_explainer = LLMExplainer()
