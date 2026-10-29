import asyncio
import json
import logging
from typing import Any

import chromadb

from app.core.config import settings
from app.ml.embeddings import embedding_engine
from app.schemas.media import RecommendationResponse
from app.services.llm_explainer import llm_explainer

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self) -> None:
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(name="media_content")

    async def get_recommendations(
        self,
        mood_query: str,
        limit: int = 5,
        exclude_ids: list[str] | None = None,
        medium_filters: list[str] | None = None,
    ) -> list[RecommendationResponse]:
        exclude_ids = exclude_ids or []
        medium_filters = medium_filters or []
        if limit < 1:
            return []

        query_embedding = await embedding_engine.generate_embedding_async(mood_query)

        where_clause: dict[str, Any] | None = None
        if len(medium_filters) == 1:
            where_clause = {"medium": medium_filters[0]}
        elif len(medium_filters) > 1:
            where_clause = {"$or": [{"medium": medium} for medium in medium_filters]}

        # Chroma rejects n_results greater than the number of matching records.
        loop = asyncio.get_running_loop()

        def _query_db() -> dict[str, Any]:
            matching_count = self.collection.count()
            if matching_count == 0:
                return {"ids": [[]], "metadatas": [[]], "distances": [[]]}
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(matching_count, limit + len(exclude_ids)),
                where=where_clause,
                include=["metadatas", "distances"],
            )

        results = await loop.run_in_executor(embedding_engine.executor, _query_db)
        ids = results.get("ids") or [[]]
        if not ids or not ids[0]:
            return []

        selected_items: list[dict[str, Any]] = []
        for index, item_id in enumerate(ids[0]):
            if item_id in exclude_ids:
                continue
            metadata = (results.get("metadatas") or [[]])[0][index] or {}
            distance = (results.get("distances") or [[]])[0][index]
            selected_items.append({"id": item_id, "meta": metadata, "distance": float(distance)})
            if len(selected_items) >= limit:
                break

        explanation_tasks = [
            llm_explainer.generate_explanation(mood_query, item["meta"], item["id"])
            for item in selected_items
        ]
        explanations = await asyncio.gather(*explanation_tasks)

        recommendations: list[RecommendationResponse] = []
        for index, item in enumerate(selected_items):
            metadata = item["meta"]
            try:
                streaming_links = json.loads(metadata.get("streaming_links") or "{}")
                if not isinstance(streaming_links, dict):
                    streaming_links = {}
            except (TypeError, json.JSONDecodeError):
                streaming_links = {}

            # This is a bounded distance-derived relevance heuristic, not a calibrated probability.
            relevance_score = max(0, min(100, round((1.0 - item["distance"] / 2.0) * 100)))
            recommendations.append(
                RecommendationResponse(
                    id=item["id"],
                    title=metadata.get("title", "Unknown Title"),
                    medium=metadata.get("medium", "Unknown Medium"),
                    themes=metadata.get("themes", "").split(", ") if metadata.get("themes") else [],
                    tone=metadata.get("tone", "nuanced"),
                    pacing=metadata.get("pacing", "moderate"),
                    ending_type=metadata.get("ending_type", "open-ended"),
                    confidence_score=relevance_score,
                    ai_explanation=explanations[index],
                    streaming_links=streaming_links,
                )
            )
        return recommendations


recommendation_service = RecommendationService()
