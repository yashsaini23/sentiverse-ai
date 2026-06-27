import os
import json
import httpx
import asyncio
from app.ml.embeddings import embedding_engine
import chromadb

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "9eaeee2107c615b20f0f0f1ec5aeffc5")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

class TMDBIngestionEngine:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="/app/chroma_data")
        self.collection = self.chroma_client.get_or_create_collection(name="media_content")

    async def fetch_trending_movies(self, page: int = 1):
        """Fetch real movie data and streaming providers from TMDB."""
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{TMDB_BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}&page={page}")
            res.raise_for_status()
            movies = res.json().get("results", [])
            
            # Fetch providers for each movie concurrently
            tasks = [self.fetch_providers(client, m["id"]) for m in movies]
            providers_list = await asyncio.gather(*tasks)
            
            return zip(movies, providers_list)

    async def fetch_providers(self, client: httpx.AsyncClient, movie_id: int):
        res = await client.get(f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}")
        data = res.json().get("results", {}).get("US", {})
        # Extract flat links for simplicity
        links = {}
        if "flatrate" in data:
            links[data["flatrate"][0]["provider_name"]] = data.get("link", "")
        return links

    async def run_ingestion(self, pages: int = 1):
        print(f"Starting TMDB Ingestion for {pages} pages...")
        documents, embeddings, metadatas, ids = [], [], [], []

        for page in range(1, pages + 1):
            movie_data = await self.fetch_trending_movies(page)
            
            for movie, providers in movie_data:
                # LLMs or heuristics would normally generate these tags; 
                # Here we map TMDB data to our emotional schema format.
                title = movie.get("title")
                overview = movie.get("overview")
                
                payload = f"Title: {title}. Description: {overview}."
                vector = await embedding_engine.generate_embedding_async(payload)
                
                documents.append(payload)
                embeddings.append(vector)
                ids.append(f"tmdb-m-{movie['id']}")
                metadatas.append({
                    "title": title,
                    "medium": "Movie",
                    "emotions": "thrilling, captivating", # Mocked for this ETL example
                    "themes": "adventure, drama",
                    "tone": "cinematic",
                    "pacing": "moderate",
                    "ending_type": "standard",
                    "streaming_links": json.dumps(providers)
                })

        # Batch Upsert into ChromaDB
        self.collection.upsert(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully ingested {len(ids)} items from TMDB into Vector Store.")

if __name__ == "__main__":
    ingester = TMDBIngestionEngine()
    asyncio.run(ingester.run_ingestion(pages=2))