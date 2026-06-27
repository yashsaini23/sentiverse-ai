from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class MoodRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Raw natural language mood input string.")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum items payload generation target count.")
    session_id: Optional[str] = Field(default="anonymous_default_user", description="Unique token representing active user state context.")
    medium_filters: List[str] = Field(default=[], description="List of media types to filter by (e.g., ['Movie', 'Anime']). Empty means no filter.")

class EmotionMetric(BaseModel):
    label: str
    score: float

class RecommendationResponse(BaseModel):
    id: str
    title: str
    medium: str
    themes: List[str] = []
    tone: str
    pacing: str
    ending_type: str
    confidence_score: int
    ai_explanation: str
    streaming_links: Dict[str, str] = Field(default_factory=dict, description="Key-Value pairs of provider names and deep links.")

class RecommendationWrapperResponse(BaseModel):
    status: str
    query_intent: str
    detected_emotions: List[EmotionMetric]
    recommendations: List[RecommendationResponse]