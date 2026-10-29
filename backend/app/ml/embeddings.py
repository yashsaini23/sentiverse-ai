import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import torch
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Loads the embedding model only when the first embedding is requested."""

    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="embedding")
        self._model: SentenceTransformer | None = None
        self._model_lock = threading.Lock()

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            with self._model_lock:
                if self._model is None:
                    logger.info("Loading embedding model %s on %s", settings.EMBEDDING_MODEL, self.device)
                    self._model = SentenceTransformer(settings.EMBEDDING_MODEL, device=self.device)
        return self._model

    def _encode(self, text: str) -> list[float]:
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()

    def generate_embedding(self, text: str) -> list[float]:
        """Synchronous interface for CLI scripts and ingestion jobs."""
        return self._encode(text)

    async def generate_embedding_async(self, text: str) -> list[float]:
        """Run model inference outside the event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._encode, text)


embedding_engine = EmbeddingEngine()
