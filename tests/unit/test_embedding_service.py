import pytest
from app.services.embedding_service import EmbeddingService


def test_get_embedding():
    text = "This is a test document for embedding."
    embedding = EmbeddingService.get_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert isinstance(embedding[0], float)

    # BAAI/bge-small-en-v1.5 has an embedding dimension of 384
    assert len(embedding) == 384


def test_get_embeddings():
    texts = ["First document.", "Second document."]
    embeddings = EmbeddingService.get_embeddings(texts)

    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert isinstance(embeddings[0], list)
    assert len(embeddings[0]) == 384
