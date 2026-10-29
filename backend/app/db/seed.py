import asyncio
from pathlib import Path

import chromadb

from app.core.config import settings
from app.ml.embeddings import embedding_engine


async def seed_database() -> None:
    db_path = Path(settings.CHROMA_DB_DIR).expanduser()
    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_or_create_collection(name="media_content")
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Media catalogue already contains {existing_count} records; skipping seed.")
        return

    dataset = [
        {"id": "m-101", "title": "Interstellar", "medium": "Movie", "description": "A team of explorers travels through a wormhole to help ensure humanity's survival.", "emotions": "lonely, hopeless, nostalgic, awe-inspiring", "themes": "cosmic isolation, father-daughter bond, sacrifice, human resilience", "tone": "melancholic, epic, hopeful", "ending_type": "bittersweet", "pacing": "slow-burn"},
        {"id": "a-201", "title": "Neon Genesis Evangelion", "medium": "Anime", "description": "A teenager pilots a bio-machine while confronting existential dread and difficult relationships.", "emotions": "empty, lonely, anxious", "themes": "existential dread, identity, connection", "tone": "bleak, cerebral, intense", "ending_type": "ambiguous", "pacing": "deliberate"},
        {"id": "g-301", "title": "Celeste", "medium": "Game", "description": "A platformer about climbing a mountain while confronting anxiety and self-doubt.", "emotions": "stressed, burnt out, anxious", "themes": "self-acceptance, overcoming adversity, mental health", "tone": "challenging, empathetic, uplifting", "ending_type": "triumphant", "pacing": "fast-paced"},
        {"id": "n-401", "title": "The Midnight Library", "medium": "Novel", "description": "A library of possible lives helps a person reconsider regret, choices, and hope.", "emotions": "heartbroken, regretful, empty", "themes": "parallel lives, conquering regret, value of life", "tone": "reflective, comforting, philosophical", "ending_type": "hopeful", "pacing": "moderate"},
        {"id": "p-501", "title": "The Anthropocene Reviewed", "medium": "Podcast", "description": "Personal essays reflect on the human condition and the beauty of everyday life.", "emotions": "nostalgic, melancholy, calm", "themes": "human condition, everyday wonder, shared history", "tone": "poetic, intimate, reassuring", "ending_type": "open-ended", "pacing": "relaxed"},
    ]

    documents, embeddings, metadatas, ids = [], [], [], []
    for item in dataset:
        document = (
            f"Title: {item['title']}. Description: {item['description']}. "
            f"Emotions: {item['emotions']}. Themes: {item['themes']}. "
            f"Tone: {item['tone']}. Pacing: {item['pacing']}."
        )
        embeddings.append(await embedding_engine.generate_embedding_async(document))
        documents.append(document)
        ids.append(item["id"])
        metadatas.append({key: item[key] for key in (
            "title", "medium", "emotions", "themes", "tone", "ending_type", "pacing"
        )})

    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    print(f"Seeded {len(ids)} media records into {db_path}.")


if __name__ == "__main__":
    asyncio.run(seed_database())
