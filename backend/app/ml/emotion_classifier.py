import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import torch
from transformers import pipeline

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmotionClassifier:
    """Loads the transformer pipeline on first use rather than during API import."""

    def __init__(self) -> None:
        self.device = 0 if torch.cuda.is_available() else -1
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="emotion")
        self._classifier: Any | None = None
        self._classifier_lock = threading.Lock()

    @property
    def classifier(self) -> Any:
        if self._classifier is None:
            with self._classifier_lock:
                if self._classifier is None:
                    logger.info("Loading emotion model %s on device %s", settings.EMOTION_MODEL, self.device)
                    self._classifier = pipeline(
                        "text-classification",
                        model=settings.EMOTION_MODEL,
                        top_k=3,
                        device=self.device,
                    )
        return self._classifier

    def _predict(self, text: str) -> list[dict[str, Any]]:
        result = self.classifier(text)
        # With top_k set, transformers returns a list of label/score dictionaries per input.
        if result and isinstance(result[0], list):
            result = result[0]
        return result

    async def detect_emotions_async(self, text: str) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._predict, text)


emotion_engine = EmotionClassifier()
