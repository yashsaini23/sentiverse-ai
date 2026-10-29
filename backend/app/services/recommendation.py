import asyncio
import json
import logging
from pathlib import Path
from collections.abc import Sequence

import chromadb

from app.core.config import settings
from app.ml.embeddings import embedding_engine
from app.schemas.media import RecommendationResponse
from app.services.llm_explainer import llm_explainer

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self) -> None:
        db_path = Path(settings.CHROMA_DB_DIR).expanduser()
        db_path.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.chroma_client.get_or_create_collection(name="media_content")

    async def get_recommendations(
        self,
        mood_query: str,
        limit: int = 5,
        exclude_ids: Sequence[str] | None = None,
        medium_filters: Sequence[str] | None = None,
    ) -> list[RecommendationResponse]:
        if not mood_query or not mood_query.strip():
            return []

        excluded = set(exclude_ids or [])
        filters = list(dict.fromkeys(medium_filters or []))
        safe_limit = max(1, min(int(limit), 20))
        collection_count = self.collection.count()
        if collection_count == 0:
            return []

        query_embedding = await embedding_engine.generate_embedding_async(mood_query)
        where_clause = None
        if len(filters) == 1:
            where_clause = {"medium": filters[0]}
        elif filters:
            where_clause = {"$or": [{"medium": medium} for medium in filters]}

        loop = asyncio.get_running_loop()
        def query_database():
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(collection_count, safe_limit + len(excluded)),
                where=where_clause,
                include=["metadatas", "distances"],
            )

        results = await loop.run_in_executor(embedding_engine.executor, query_database)
        ids = (results.get("ids") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]

        selected = []
        for index, item_id in enumerate(ids):
            if item_id in excluded:
                continue
            selected.append({
                "id": item_id,
                "meta": metadatas[index] or {},
                "distance": float(distances[index] or 0.0),
            })
            if len(selected) >= safe_limit:
                break
        if not selected:
            return []

        explanations = await asyncio.gather(*[
            llm_explainer.generate_explanation(mood_query, item["meta"], item["id"])
            for item in selected
        ])

        recommendations = []
        for index, item in enumerate(selected):
            meta = item["meta"]
            distance = item["distance"]
            confidence = max(0, min(100, round((1.0 - distance / 2.0) * 100)))
            raw_links = meta.get("streaming_links", {})
            if isinstance(raw_links, str):
                try:
                    raw_links = json.loads(raw_links)
                except (TypeError, json.JSONDecodeError):
                    raw_links = {}
            streaming_links = raw_links if isinstance(raw_links, dict) else {}
            raw_themes = meta.get("themes", "")
            themes = raw_themes if isinstance(raw_themes, list) else [
                part.strip() for part in str(raw_themes).split(",") if part.strip()
            ]
            recommendations.append(RecommendationResponse(
                id=item["id"],
                title=meta.get("title", "Unknown Title"),
                medium=meta.get("medium", "Unknown Medium"),
                themes=themes,
                tone=meta.get("tone", "nuanced"),
                pacing=meta.get("pacing", "moderate"),
                ending_type=meta.get("ending_type", "open-ended"),
                confidence_score=confidence,
                ai_explanation=explanations[index],
                streaming_links=streaming_links,
            ))
        return recommendations


recommendation_service = RecommendationService()
