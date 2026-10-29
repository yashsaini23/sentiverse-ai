import asyncio
import json
import os

import chromadb
import httpx

from app.core.config import settings
from app.ml.embeddings import embedding_engine

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


class TMDBIngestionEngine:
    def __init__(self) -> None:
        db_path = os.path.abspath(os.path.expanduser(settings.CHROMA_DB_DIR))
        os.makedirs(db_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="media_content")

    async def _get(self, client: httpx.AsyncClient, path: str, **params):
        if not TMDB_API_KEY:
            raise RuntimeError("Set TMDB_API_KEY in the environment before running ingestion.")
        response = await client.get(
            f"{TMDB_BASE_URL}{path}",
            params={"api_key": TMDB_API_KEY, **params},
        )
        response.raise_for_status()
        return response.json()

    async def fetch_trending_movies(self, client: httpx.AsyncClient, page: int = 1):
        data = await self._get(client, "/trending/movie/week", page=page)
        movies = data.get("results", [])
        providers = await asyncio.gather(
            *(self.fetch_providers(client, movie["id"]) for movie in movies)
        )
        return list(zip(movies, providers))

    async def fetch_providers(self, client: httpx.AsyncClient, movie_id: int) -> dict[str, str]:
        data = await self._get(client, f"/movie/{movie_id}/watch/providers")
        region = data.get("results", {}).get("US", {})
        link = region.get("link", "")
        return {
            provider["provider_name"]: link
            for provider in region.get("flatrate", [])
            if provider.get("provider_name")
        }

    async def run_ingestion(self, pages: int = 1) -> None:
        documents, embeddings, metadatas, ids = [], [], [], []
        async with httpx.AsyncClient(timeout=20.0) as client:
            for page in range(1, max(1, pages) + 1):
                for movie, providers in await self.fetch_trending_movies(client, page):
                    title = movie.get("title") or "Untitled"
                    overview = movie.get("overview") or ""
                    document = f"Title: {title}. Description: {overview}."
                    documents.append(document)
                    embeddings.append(await embedding_engine.generate_embedding_async(document))
                    ids.append(f"tmdb-m-{movie['id']}")
                    metadatas.append({
                        "title": title,
                        "medium": "Movie",
                        "emotions": "thrilling, captivating",
                        "themes": "adventure, drama",
                        "tone": "cinematic",
                        "pacing": "moderate",
                        "ending_type": "standard",
                        "streaming_links": json.dumps(providers),
                    })
        if ids:
            self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        print(f"Successfully ingested {len(ids)} TMDB items.")


if __name__ == "__main__":
    asyncio.run(TMDBIngestionEngine().run_ingestion(pages=2))
