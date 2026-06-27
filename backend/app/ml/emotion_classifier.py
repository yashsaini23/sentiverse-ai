from transformers import pipeline
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import torch

logger = logging.getLogger(__name__)

class EmotionClassifier:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Loading Emotion Classifier on device {self.device}...")
        # SamLowe's roberta-base is highly optimized for 28 distinct emotional categories
        self.classifier = pipeline(
            "text-classification", 
            model="SamLowe/roberta-base-go_emotions", 
            top_k=3, 
            device=self.device
        )
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _predict(self, text: str) -> list[dict]:
        return self.classifier(text)[0]

    async def detect_emotions_async(self, text: str) -> list[dict]:
        """Returns the top 3 detected emotions and their confidence scores."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._predict, text)

emotion_engine = EmotionClassifier()