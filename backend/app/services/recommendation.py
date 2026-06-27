import asyncio
import chromadb
import json
from typing import List
from app.ml.embeddings import embedding_engine
from app.schemas.media import RecommendationResponse
from app.services.llm_explainer import llm_explainer

class RecommendationService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="/app/chroma_data")
        self.collection = self.chroma_client.get_or_create_collection(name="media_content")

    async def get_recommendations(
        self, 
        mood_query: str, 
        limit: int = 5, 
        exclude_ids: List[str] = None,
        medium_filters: List[str] = None
    ) -> List[RecommendationResponse]:
        
        if exclude_ids is None: exclude_ids = []
        if medium_filters is None: medium_filters = []

        # 1. Generate Embeddings
        query_embedding = await embedding_engine.generate_embedding_async(mood_query)

        # 2. Database Filtering
        where_clause = None
        if medium_filters:
            if len(medium_filters) == 1:
                where_clause = {"medium": medium_filters[0]}
            else:
                where_clause = {"$or": [{"medium": m} for m in medium_filters]}

        fetch_limit = limit + len(exclude_ids)
        loop = asyncio.get_running_loop()
        
        def _query_db():
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=fetch_limit,
                where=where_clause,
                include=["metadatas", "distances"]
            )

        results = await loop.run_in_executor(embedding_engine.executor, _query_db)

        if not results['ids'] or not results['ids'][0]:
            return []

        # 3. Filter History and Extract Metadata
        selected_items = []
        for i in range(len(results['ids'][0])):
            item_id = results['ids'][0][i]
            if item_id in exclude_ids:
                continue
            
            selected_items.append({
                "id": item_id,
                "meta": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
            if len(selected_items) == limit:
                break

        # 4. Generate LLM Explanations in PARALLEL
        explanation_tasks = [
            llm_explainer.generate_explanation(mood_query, item["meta"]) 
            for item in selected_items
        ]
        
        # This executes all LLM API calls simultaneously
        explanations = await asyncio.gather(*explanation_tasks)

        # 5. Build Final Response Objects
        recommendations: List[RecommendationResponse] = []
        
        for idx, item in enumerate(selected_items):
            meta = item["meta"]
            distance = item["distance"]
            confidence = max(0, min(100, int((1.0 - (distance / 2.0)) * 100)))

            try:
                streaming_links = json.loads(meta.get("streaming_links", "{}"))
            except Exception:
                streaming_links = {}

            recommendations.append(RecommendationResponse(
                id=item["id"],
                title=meta.get("title", "Unknown Title"),
                medium=meta.get("medium", "Unknown Medium"),
                themes=meta.get("themes", "").split(", ") if meta.get("themes") else [],
                tone=meta.get("tone", "nuanced"),
                pacing=meta.get("pacing", "moderate"),
                ending_type=meta.get("ending_type", "open-ended"),
                confidence_score=confidence,
                ai_explanation=explanations[idx], # Using the dynamically generated LLM text
                streaming_links=streaming_links
            ))
        
        return recommendations

recommendation_service = RecommendationService()