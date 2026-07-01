# mypy: ignore-errors
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.endpoints.query import get_vector_store
from app.storage.vector_store import VectorStore
from app.schemas.document import DocumentChunk
from app.core.config import settings
import os
import shutil


@pytest.fixture(scope="module")
def test_query_db() -> None:
    original_path = settings.vector_db_path
    test_path = "data/test_query_lancedb"
    settings.vector_db_path = test_path

    store = VectorStore(table_name="query_chunks")

    # Insert some dummy chunks for testing retrieval
    chunks = [
        DocumentChunk(
            chunk_id="q_chunk1",
            document_path="history.pdf",
            page_number=1,
            text="The Eiffel Tower is in Paris.",
            metadata={},
        ),
        DocumentChunk(
            chunk_id="q_chunk2",
            document_path="science.pdf",
            page_number=2,
            text="Water boils at 100 degrees Celsius.",
            metadata={},
        ),
    ]
    store.add_chunks(chunks)

    yield store

    settings.vector_db_path = original_path
    if os.path.exists(test_path):
        shutil.rmtree(test_path)


@pytest.fixture(scope="module")
def client(test_query_db):
    app.dependency_overrides[get_vector_store] = lambda: test_query_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_query_api(client, monkeypatch) -> None:
    # Mock LLMService.generate_response to avoid actual network call to Ollama
    async def mock_generate(prompt: str) -> str:
        return "Based on the context, the Eiffel Tower is in Paris."

    from app.services.llm_service import LLMService

    monkeypatch.setattr(LLMService, "generate_response", mock_generate)

    response = client.post(
        "/api/v1/query", json={"query": "Where is the Eiffel Tower?"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["answer"] == "Based on the context, the Eiffel Tower is in Paris."
    assert len(data["sources"]) > 0
    assert data["sources"][0]["document_path"] == "history.pdf"
