import asyncio
import logging

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.memory import memory_manager
from app.core.sanitizer import InputSanitizer
from app.core.security import rate_limiter
from app.ml.emotion_classifier import emotion_engine
from app.schemas.media import EmotionMetric, MoodRequest, RecommendationWrapperResponse
from app.services.recommendation import recommendation_service
from app.services.media_provider_hub import media_provider_hub

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous NLP-driven entertainment recommendation API.",
    version=settings.VERSION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.post("/api/v1/recommend", response_model=RecommendationWrapperResponse)
async def recommend_media(
    request: MoodRequest,
    _rate_limit: None = Depends(rate_limiter.check_rate_limit),
) -> RecommendationWrapperResponse:
    query = InputSanitizer.clean_mood_query(request.query)
    if not query:
        raise HTTPException(status_code=400, detail="The query is empty after input validation.")

    try:
        try:
            context = await memory_manager.get_user_context(request.session_id)
        except Exception:
            logger.warning("Session memory unavailable; continuing without history.", exc_info=True)
            context = {"seen_items": [], "mood_history": []}

        async def get_media():
            try:
                live = await media_provider_hub.recommend(
                    query=query,
                    limit=request.limit,
                    medium_filters=request.medium_filters,
                    region=request.region,
                    language=request.language,
                )
                seen = set(context.get("seen_items", []))
                fresh = [item for item in live if item.id not in seen]
                if fresh:
                    return fresh
                if live:
                    return live
            except httpx.HTTPError:
                logger.exception("A live media provider failed; falling back to local catalogue.")
            return await recommendation_service.get_recommendations(
                mood_query=query,
                limit=request.limit,
                exclude_ids=context.get("seen_items", []),
                medium_filters=request.medium_filters,
            )

        recommendations, emotions = await asyncio.gather(
            get_media(),
            emotion_engine.detect_emotions_async(query),
        )

        try:
            await memory_manager.update_user_context(
                session_id=request.session_id,
                new_mood=query,
                new_items=[item.id for item in recommendations],
            )
        except Exception:
            logger.warning("Session memory update failed.", exc_info=True)

        return RecommendationWrapperResponse(
            status="success",
            query_intent=query,
            detected_emotions=[EmotionMetric(label=e["label"], score=e["score"]) for e in emotions],
            recommendations=recommendations,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Recommendation pipeline failed.")
        raise HTTPException(status_code=500, detail="The recommendation pipeline encountered an internal error.") from exc


@app.get("/health", summary="System health check", tags=["Diagnostics"])
async def health_check() -> dict[str, str]:
    return {
        "status": "operational",
        "engine": f"{settings.PROJECT_NAME} v{settings.VERSION}",
        "environment": settings.ENVIRONMENT,
    }
