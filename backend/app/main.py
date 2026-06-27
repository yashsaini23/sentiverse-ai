import asyncio
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

# --- Core Infrastructure Imports ---
from app.core.config import settings
from app.core.sanitizer import InputSanitizer
from app.core.memory import memory_manager
from app.core.security import rate_limiter

# --- AI & Business Logic Imports ---
from app.services.recommendation import recommendation_service
from app.ml.emotion_classifier import emotion_engine

# --- Strict Schema Imports ---
from app.schemas.media import (
    MoodRequest, 
    RecommendationWrapperResponse, 
    EmotionMetric
)

# Initialize FastAPI Application with metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous NLP-Driven Sentiment Recommendation Microservice",
    version=settings.VERSION
)

# Cross-Origin Resource Sharing Protocol (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    # In production, replace ["*"] with your exact Next.js frontend domain (e.g., ["https://sentiverse.com"])
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/api/v1/recommend", 
    response_model=RecommendationWrapperResponse,
    summary="Generate AI Emotion Recommendations",
    description="Processes raw user mood, extracts emotion tensors, queries vector DB, and generates LLM context."
)
async def recommend_media(
    request: MoodRequest, 
    http_request: Request,
    _ = Depends(rate_limiter.check_rate_limit)  # Security: Executes Rate Limiter before any AI processing
):
    """
    Primary orchestration API endpoint. 
    Maintains low latency by checking session context caches, cleaning input text, 
    and running the vector engine and classification pipelines in parallel.
    """
    # 1. Sanitize raw text to defend internal transformers from injection exploits
    sanitized_query = InputSanitizer.clean_mood_query(request.query)
    if not sanitized_query:
        raise HTTPException(
            status_code=400, 
            detail="Provided query contains invalid character combinations or zero valid tokens after sanitization pass."
        )
    
    try:
        # 2. Retrieve history context vectors from Redis state infrastructure
        user_context = await memory_manager.get_user_context(request.session_id)
        seen_items = user_context.get("seen_items", [])

        # 3. Deploy concurrent pipeline workers across the system thread pool
        recommendation_task = recommendation_service.get_recommendations(
            mood_query=sanitized_query,
            limit=request.limit,
            exclude_ids=seen_items,
            medium_filters=request.medium_filters
        )
        emotion_detection_task = emotion_engine.detect_emotions_async(sanitized_query)

        # Execute operations in parallel to optimize target latency budgets
        recommendations, explicit_emotions = await asyncio.gather(
            recommendation_task, 
            emotion_detection_task
        )

        # 4. Format classification payloads safely for schema matching boundaries
        formatted_emotions = [
            EmotionMetric(label=e["label"], score=e["score"]) for e in explicit_emotions
        ]

        # 5. Asynchronously update the user's history cache in Redis without delaying response generation
        recommended_ids = [item.id for item in recommendations]
        asyncio.create_task(
            memory_manager.update_user_context(
                session_id=request.session_id,
                new_mood=sanitized_query,
                new_items=recommended_ids
            )
        )

        # 6. Emit complete structural system validation metrics
        return RecommendationWrapperResponse(
            status="success",
            query_intent=sanitized_query,
            detected_emotions=formatted_emotions,
            recommendations=recommendations
        )

    except Exception as systemic_exception:
        # Log error traces internally and return a standardized HTTP exception response
        # Production loggers must append structured traceback information here
        raise HTTPException(
            status_code=500,
            detail=f"A processing error occurred inside the AI pipeline: {str(systemic_exception)}"
        )

@app.get(
    "/health", 
    summary="System Health Check",
    tags=["Diagnostics"]
)
async def health_check():
    """System heartbeat verification interface for Docker/Kubernetes probes."""
    return {
        "status": "operational", 
        "engine": f"{settings.PROJECT_NAME} v{settings.VERSION}",
        "environment": settings.ENVIRONMENT
    }