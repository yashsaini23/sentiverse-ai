import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer
import torch
import logging

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Loading embedding model on {self.device}...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        # Dedicated thread pool executor for heavy tensor computations
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _encode(self, text: str) -> list[float]:
        # Enforce model-level truncation safely
        return self.model.encode(text, convert_to_numpy=True).tolist()

    async def generate_embedding_async(self, text: str) -> list[float]:
        """Offloads heavy tensor computation to a managed thread pool."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._encode, text)

embedding_engine = EmbeddingEngine()