from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging_config import logger

class LocalEmbeddingModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalEmbeddingModel, cls).__new__(cls)
            logger.info(f"Loading local embedding model: '{settings.EMBEDDING_MODEL}'")
            cls._instance.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully.")
        return cls._instance

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def encode_single(self, text: str) -> List[float]:
        return self.encode([text])[0]
