import asyncio
import json
import os

import chromadb
import httpx

from app.core.config import settings
from app.ml.embeddings import embedding_engine

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_REGION = os.getenv("TMDB_REGION", "US")


class TMDBIngestionEngine:
    def __init__(self) -> None:
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(name="media_content")

    @staticmethod
    def _require_api_key() -> str:
        if not TMDB_API_KEY:
            raise RuntimeError("TMDB_API_KEY is required to ingest TMDB content.")
        return TMDB_API_KEY

    async def fetch_trending_movies(self, client: httpx.AsyncClient, page: int = 1):
        response = await client.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={"api_key": self._require_api_key(), "page": page},
        )
        response.raise_for_status()
        movies = response.json().get("results", [])
        providers = await asyncio.gather(
            *(self.fetch_providers(client, movie["id"]) for movie in movies)
        )
        return list(zip(movies, providers))

    async def fetch_providers(self, client: httpx.AsyncClient, movie_id: int) -> dict[str, str]:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers",
            params={"api_key": self._require_api_key()},
        )
        response.raise_for_status()
        data = response.json().get("results", {}).get(TMDB_REGION, {})
        providers = data.get("flatrate", [])
        if providers and data.get("link"):
            return {providers[0]["provider_name"]: data["link"]}
        return {}

    async def run_ingestion(self, pages: int = 1) -> None:
        documents, embeddings, metadatas, ids = [], [], [], []
        async with httpx.AsyncClient(timeout=20.0) as client:
            for page in range(1, pages + 1):
                for movie, providers in await self.fetch_trending_movies(client, page):
                    title = movie.get("title") or "Untitled"
                    payload = f"Title: {title}. Description: {movie.get('overview') or ''}."
                    embeddings.append(await embedding_engine.generate_embedding_async(payload))
                    documents.append(payload)
                    ids.append(f"tmdb-m-{movie['id']}")
                    metadatas.append({
                        "title": title, "medium": "Movie",
                        "emotions": "thrilling, captivating", "themes": "adventure, drama",
                        "tone": "cinematic", "pacing": "moderate", "ending_type": "standard",
                        "streaming_links": json.dumps(providers),
                    })

        if ids:
            self.collection.upsert(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
        print(f"Successfully ingested {len(ids)} items from TMDB.")


if __name__ == "__main__":
    asyncio.run(TMDBIngestionEngine().run_ingestion(pages=2))
