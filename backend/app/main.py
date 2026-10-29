import asyncio
import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.memory import memory_manager
from app.core.sanitizer import InputSanitizer
from app.core.security import rate_limiter
from app.ml.emotion_classifier import emotion_engine
from app.schemas.media import EmotionMetric, MoodRequest, RecommendationWrapperResponse
from app.services.recommendation import recommendation_service

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous NLP-driven sentiment recommendation service",
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.post("/api/v1/recommend", response_model=RecommendationWrapperResponse, summary="Generate AI emotion recommendations")
async def recommend_media(
    request: MoodRequest,
    http_request: Request,
    _=Depends(rate_limiter.check_rate_limit),
) -> RecommendationWrapperResponse:
    sanitized_query = InputSanitizer.clean_mood_query(request.query)
    if not sanitized_query:
        raise HTTPException(status_code=400, detail="Please provide a mood description with valid text.")

    session_id = request.session_id or "anonymous_default_user"
    try:
        user_context = await memory_manager.get_user_context(session_id)
        seen_items = user_context.get("seen_items", [])

        recommendations, detected_emotions = await asyncio.gather(
            recommendation_service.get_recommendations(
                mood_query=sanitized_query,
                limit=request.limit,
                exclude_ids=seen_items,
                medium_filters=request.medium_filters,
            ),
            emotion_engine.detect_emotions_async(sanitized_query),
        )

        formatted_emotions = [
            EmotionMetric(label=emotion["label"], score=emotion["score"])
            for emotion in detected_emotions
        ]
        asyncio.create_task(
            memory_manager.update_user_context(
                session_id=session_id,
                new_mood=sanitized_query,
                new_items=[item.id for item in recommendations],
            )
        )
        return RecommendationWrapperResponse(
            status="success",
            query_intent=sanitized_query,
            detected_emotions=formatted_emotions,
            recommendations=recommendations,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Recommendation pipeline failed")
        raise HTTPException(
            status_code=500,
            detail="The recommendation service encountered an internal error. Please try again later.",
        ) from None


@app.get("/health", summary="System health check", tags=["Diagnostics"])
async def health_check() -> dict[str, str]:
    return {
        "status": "operational",
        "engine": f"{settings.PROJECT_NAME} v{settings.VERSION}",
        "environment": settings.ENVIRONMENT,
    }
