import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import torch
from transformers import pipeline

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmotionClassifier:
    """Lazy-loaded emotion model with a consistent list-of-dicts result."""

    def __init__(self) -> None:
        self.device = 0 if torch.cuda.is_available() else -1
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="emotion")
        self._classifier = None
        self._lock = threading.Lock()

    def _get_classifier(self):
        if self._classifier is None:
            with self._lock:
                if self._classifier is None:
                    logger.info("Loading emotion classifier on device %s", self.device)
                    self._classifier = pipeline(
                        "text-classification",
                        model=settings.EMOTION_MODEL,
                        top_k=3,
                        device=self.device,
                    )
        return self._classifier

    def _predict(self, text: str) -> list[dict]:
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")
        result = self._get_classifier()(text.strip())
        if result and isinstance(result[0], list):
            result = result[0]
        return [{"label": str(item["label"]), "score": float(item["score"])} for item in result[:3]]

    async def detect_emotions_async(self, text: str) -> list[dict]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._predict, text)

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)


emotion_engine = EmotionClassifier()
