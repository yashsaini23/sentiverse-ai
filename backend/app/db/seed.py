import sys
import os
# Ensure app directory is accessible via Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import chromadb
from app.ml.embeddings import embedding_engine

def seed_database():
    print("Initializing ChromaDB Persistent Client for Seeding...")
    chroma_client = chromadb.PersistentClient(path="/app/chroma_data")
    
    # Force delete existing collection to prevent duplication during re-runs
    try:
        chroma_client.delete_collection("media_content")
        print("Cleared existing collection.")
    except Exception:
        pass

    collection = chroma_client.create_collection(name="media_content")

    # Production-ready semantic mock dataset spanning multiple mediums
    dataset = [
        {
            "id": "m-101",
            "title": "Interstellar",
            "medium": "Movie",
            "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival amid global famine and isolation.",
            "emotions": "lonely, hopeless, nostalgic, awe-inspiring",
            "themes": "cosmic isolation, father-daughter bond, sacrifice, human resilience",
            "tone": "melancholic, epic, hopeful",
            "ending_type": "bittersweet",
            "pacing": "slow-burn"
        },
        {
            "id": "a-201",
            "title": "Neon Genesis Evangelion",
            "medium": "Anime",
            "description": "A teenage boy is recruited by his distant father to pilot a giant bio-machine mecha into combat against alien entities, triggering deep existential dread.",
            "emotions": "empty, dark psychological story, lonely, anxious",
            "themes": "existential dread, depression, hedgehog's dilemma, identity",
            "tone": "bleak, cerebral, intense",
            "ending_type": "ambiguous",
            "pacing": "deliberate"
        },
        {
            "id": "g-301",
            "title": "Celeste",
            "medium": "Game",
            "description": "A narrative-driven platformer about a young woman climbing a mystical mountain while confronting her personified panic attacks and depression.",
            "emotions": "stressed, burnt out, need motivation, anxious",
            "themes": "mental health awareness, self-acceptance, overcoming adversity",
            "tone": "challenging, empathetic, uplifting",
            "ending_type": "triumphant",
            "pacing": "fast-paced"
        },
        {
            "id": "n-401",
            "title": "The Midnight Library",
            "medium": "Novel",
            "description": "Between life and death there is a library containing an infinite number of books, each telling the story of another reality you could have lived if you made different choices.",
            "emotions": "heartbroken, regretful, empty, need hope",
            "themes": "parallel universes, conquering regret, value of life",
            "tone": "reflective, comforting, philosophical",
            "ending_type": "hopeful",
            "pacing": "moderate"
        },
        {
            "id": "p-501",
            "title": "The Anthropocene Reviewed",
            "medium": "Podcast",
            "description": "Deeply personal essays reviewing facets of our human-centered planet on a five-star scale, analyzing everything from sunsets to pandemics.",
            "emotions": "nostalgic, melancholy, calm, looking for beauty",
            "themes": "human condition, everyday wonder, shared history",
            "tone": "poetic, intimate, reassuring",
            "ending_type": "open-ended",
            "pacing": "relaxed"
        }
    ]

    print(f"Generating semantic embeddings for {len(dataset)} items...")
    
    documents = []
    embeddings = []
    metadatas = []
    ids = []

    for item in dataset:
        # Construct a dense text payload combining all metadata vectors for structural parsing
        payload = f"Title: {item['title']}. Description: {item['description']}. Emotions: {item['emotions']}. Themes: {item['themes']}. Tone: {item['tone']}. Pacing: {item['pacing']}."
        
        # Calculate vector embedding across the sentence space
        vector = embedding_engine.generate_embedding(payload)
        
        documents.append(payload)
        embeddings.append(vector)
        metadatas.append({
            "title": item["title"],
            "medium": item["medium"],
            "emotions": item["emotions"],
            "themes": item["themes"],
            "tone": item["tone"],
            "ending_type": item["ending_type"],
            "pacing": item["pacing"]
        })
        ids.append(item["id"])

    # Batch add into vector engine
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Vector database successfully seeded with initial emotional schemas!")

if __name__ == "__main__":
    seed_database()