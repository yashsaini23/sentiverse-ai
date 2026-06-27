import os
import asyncio
import hashlib
import logging
from openai import AsyncOpenAI
from app.core.memory import memory_manager

logger = logging.getLogger(__name__)

class LLMExplainer:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "missing_key"),
        )
        self.model = "gpt-3.5-turbo"
        # Cache Time-To-Live: 7 days
        self.cache_ttl = 604800 

    def _generate_cache_key(self, mood: str, media_id: str) -> str:
        """Generates a deterministic hash key for Redis caching."""
        mood_hash = hashlib.md5(mood.strip().lower().encode()).hexdigest()
        return f"llm_cache:{media_id}:{mood_hash}"

    async def generate_explanation(self, user_mood: str, media_meta: dict, media_id: str) -> str:
        """
        Fetches an empathetic explanation from Redis cache if available, 
        otherwise generates it via LLM and caches the result.
        """
        cache_key = self._generate_cache_key(user_mood, media_id)
        
        # 1. Check Redis Cache First
        try:
            cached_explanation = await memory_manager.redis.get(cache_key)
            if cached_explanation:
                return cached_explanation
        except Exception as e:
            logger.warning(f"Redis cache read failed: {str(e)}")

        # 2. LLM Generation Fallback
        title = media_meta.get("title", "this title")
        medium = media_meta.get("medium", "item")
        themes = media_meta.get("themes", "complex themes")
        tone = media_meta.get("tone", "nuanced")

        system_prompt = (
            "You are SentiVerse, an empathetic AI entertainment curator. "
            "Explain to the user WHY you recommended this specific piece of media based on their mood. "
            "Rules:\n"
            "1. Be empathetic. Validate their feelings.\n"
            "2. Keep it to exactly two concise, comforting sentences.\n"
            "3. Mention the media's themes or tone and how it helps their current state.\n"
            "4. Speak naturally, directly to the user."
        )

        user_prompt = (
            f"User's mood: '{user_mood}'\n"
            f"Recommended {medium}: '{title}'\n"
            f"Media Themes: {themes}\n"
            f"Media Tone: {tone}\n\n"
            f"Write the explanation."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=80,
                temperature=0.7,
            )
            explanation = response.choices[0].message.content.strip()
            
            # 3. Save to Redis Cache Asynchronously
            asyncio.create_task(
                memory_manager.redis.setex(cache_key, self.cache_ttl, explanation)
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"LLM Explanation failed: {str(e)}")
            return (
                f"The themes of {themes} in this {medium.lower()} deeply align "
                f"with your feeling of '{user_mood}'."
            )

llm_explainer = LLMExplainer()