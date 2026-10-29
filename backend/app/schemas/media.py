from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MoodRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural-language mood description.")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of recommendations.")
    session_id: Optional[str] = Field(default="anonymous_default_user", max_length=128)
    medium_filters: List[str] = Field(
        default_factory=list,
        description="Optional media type filters, such as Movie or Anime.",
    )


class EmotionMetric(BaseModel):
    label: str
    score: float = Field(ge=0.0, le=1.0)


class RecommendationResponse(BaseModel):
    id: str
    title: str
    medium: str
    themes: List[str] = Field(default_factory=list)
    tone: str
    pacing: str
    ending_type: str
    confidence_score: int = Field(ge=0, le=100, description="Distance-derived relevance heuristic, not a probability.")
    ai_explanation: str
    streaming_links: Dict[str, str] = Field(
        default_factory=dict,
        description="Streaming provider names mapped to deep links.",
    )


class RecommendationWrapperResponse(BaseModel):
    status: str
    query_intent: str
    detected_emotions: List[EmotionMetric]
    recommendations: List[RecommendationResponse]
