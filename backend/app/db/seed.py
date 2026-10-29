import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import chromadb

from app.core.config import settings
from app.ml.embeddings import embedding_engine


def seed_database() -> None:
    print("Initializing ChromaDB persistent client for seeding...")
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
    try:
        client.delete_collection("media_content")
        print("Cleared existing collection.")
    except Exception:
        pass
    collection = client.create_collection(name="media_content")

    dataset = [
        {"id": "m-101", "title": "Interstellar", "medium": "Movie",
         "description": "A team of explorers travel through a wormhole in space to help ensure humanity's survival.",
         "emotions": "lonely, hopeless, nostalgic, awe-inspiring",
         "themes": "cosmic isolation, father-daughter bond, sacrifice, human resilience",
         "tone": "melancholic, epic, hopeful", "ending_type": "bittersweet", "pacing": "slow-burn"},
        {"id": "a-201", "title": "Neon Genesis Evangelion", "medium": "Anime",
         "description": "A teenage boy pilots a giant bio-machine and confronts existential dread and identity.",
         "emotions": "empty, dark psychological story, lonely, anxious",
         "themes": "existential dread, depression, identity",
         "tone": "bleak, cerebral, intense", "ending_type": "ambiguous", "pacing": "deliberate"},
        {"id": "g-301", "title": "Celeste", "medium": "Game",
         "description": "A platformer about climbing a mountain while confronting panic and depression.",
         "emotions": "stressed, burnt out, need motivation, anxious",
         "themes": "mental health awareness, self-acceptance, overcoming adversity",
         "tone": "challenging, empathetic, uplifting", "ending_type": "triumphant", "pacing": "fast-paced"},
        {"id": "n-401", "title": "The Midnight Library", "medium": "Novel",
         "description": "A library between life and death contains books about lives shaped by different choices.",
         "emotions": "heartbroken, regretful, empty, need hope",
         "themes": "parallel universes, conquering regret, value of life",
         "tone": "reflective, comforting, philosophical", "ending_type": "hopeful", "pacing": "moderate"},
        {"id": "p-501", "title": "The Anthropocene Reviewed", "medium": "Podcast",
         "description": "Personal essays review facets of the human-centered planet, from sunsets to pandemics.",
         "emotions": "nostalgic, melancholy, calm, looking for beauty",
         "themes": "human condition, everyday wonder, shared history",
         "tone": "poetic, intimate, reassuring", "ending_type": "open-ended", "pacing": "relaxed"},
    ]

    documents, embeddings, metadatas, ids = [], [], [], []
    for item in dataset:
        payload = (
            f"Title: {item['title']}. Description: {item['description']}. "
            f"Emotions: {item['emotions']}. Themes: {item['themes']}. "
            f"Tone: {item['tone']}. Pacing: {item['pacing']}."
        )
        embeddings.append(embedding_engine.generate_embedding(payload))
        documents.append(payload)
        metadatas.append({key: item[key] for key in (
            "title", "medium", "emotions", "themes", "tone", "ending_type", "pacing"
        )})
        ids.append(item["id"])

    collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
    print(f"Vector database seeded with {len(ids)} items.")


if __name__ == "__main__":
    seed_database()
