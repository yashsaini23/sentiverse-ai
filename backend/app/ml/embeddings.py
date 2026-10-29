import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import torch
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Load the embedding model only when inference is first requested."""

    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="embedding")
        self._model = None
        self._lock = threading.Lock()

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info("Loading embedding model on %s", self.device)
                    self._model = SentenceTransformer(settings.EMBEDDING_MODEL, device=self.device)
        return self._model

    def _encode(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")
        return self._get_model().encode(text.strip(), convert_to_numpy=True).tolist()

    async def generate_embedding_async(self, text: str) -> list[float]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._encode, text)

    def generate_embedding(self, text: str) -> list[float]:
        return self._encode(text)

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)


embedding_engine = EmbeddingEngine()
