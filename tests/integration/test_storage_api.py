import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.endpoints.storage import get_vector_store
from app.storage.vector_store import VectorStore
from app.core.config import settings
import os
import shutil
import io

# Setup test DB
@pytest.fixture(scope="module")
def test_db():
    original_path = settings.vector_db_path
    test_path = "data/test_api_lancedb"
    settings.vector_db_path = test_path
    
    # We must explicitly create and yield the store
    store = VectorStore(table_name="api_chunks")
    
    yield store
    
    settings.vector_db_path = original_path
    if os.path.exists(test_path):
        shutil.rmtree(test_path)

@pytest.fixture(scope="module")
def client(test_db):
    # Override the dependency so API uses the test DB
    app.dependency_overrides[get_vector_store] = lambda: test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_ingest_markdown(client):
    content = b"# Integration Test\n\nThis is an integration test for the API."
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("test_doc.md", io.BytesIO(content), "text/markdown")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document ingested successfully"
    assert data["document_path"] == "test_doc.md"
    assert data["num_pages"] == 1
    assert data["num_chunks"] >= 1

def test_list_documents(client):
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["documents"]) == 1
    doc = data["documents"][0]
    assert doc["document_path"] == "test_doc.md"
    assert doc["num_chunks"] >= 1

def test_delete_document(client):
    response = client.delete("/api/v1/documents/test_doc.md")
    assert response.status_code == 200
    assert response.json()["document_path"] == "test_doc.md"
    
    # Verify it's gone
    list_response = client.get("/api/v1/documents")
    assert len(list_response.json()["documents"]) == 0
