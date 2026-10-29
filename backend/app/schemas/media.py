from pydantic import BaseModel, Field, field_validator


class MoodRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural-language mood description.")
    limit: int = Field(default=5, ge=1, le=20)
    session_id: str = Field(default="anonymous_default_user", min_length=1, max_length=128)
    medium_filters: list[str] = Field(default_factory=list)

    @field_validator("medium_filters")
    @classmethod
    def clean_medium_filters(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip() for value in values if value and value.strip()))


class EmotionMetric(BaseModel):
    label: str
    score: float = Field(ge=0.0, le=1.0)


class RecommendationResponse(BaseModel):
    id: str
    title: str
    medium: str
    themes: list[str] = Field(default_factory=list)
    tone: str = "nuanced"
    pacing: str = "moderate"
    ending_type: str = "open-ended"
    confidence_score: int = Field(ge=0, le=100)
    ai_explanation: str
    streaming_links: dict[str, str] = Field(default_factory=dict)
    poster_url: str | None = None
    backdrop_url: str | None = None
    overview: str | None = None
    release_year: str | None = None
    vote_average: float | None = None


class RecommendationWrapperResponse(BaseModel):
    status: str
    query_intent: str
    detected_emotions: list[EmotionMetric] = Field(default_factory=list)
    recommendations: list[RecommendationResponse] = Field(default_factory=list)
