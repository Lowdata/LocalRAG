from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class EmbeddingService:
    _model: SentenceTransformer | None = None

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            # We initialize the model lazily to speed up cold starts
            cls._model = SentenceTransformer(settings.embedding_model)
        return cls._model

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """Generate an embedding for a single text string."""
        model = cls._get_model()
        # encode returns a numpy array, we convert to a standard python list of floats
        return model.encode(text).tolist()

    @classmethod
    def get_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text strings."""
        model = cls._get_model()
        return model.encode(texts).tolist()
