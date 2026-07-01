import pytest
import os
import shutil
from app.schemas.document import DocumentChunk
from app.schemas.vector import ChunkRecord
from app.storage.vector_store import VectorStore
from app.core.config import settings

@pytest.fixture(autouse=True)
def setup_test_db():
    # Use a temporary db for testing
    original_path = settings.vector_db_path
    test_path = "data/test_lancedb"
    settings.vector_db_path = test_path
    
    yield
    
    # Cleanup after test
    settings.vector_db_path = original_path
    if os.path.exists(test_path):
        shutil.rmtree(test_path)

def test_vector_store_add_and_search():
    store = VectorStore(table_name="test_chunks")
    
    # Create dummy chunks
    chunks = [
        DocumentChunk(
            chunk_id="chunk1",
            document_path="test1.pdf",
            page_number=1,
            text="The capital of France is Paris.",
            metadata={"author": "John"}
        ),
        DocumentChunk(
            chunk_id="chunk2",
            document_path="test2.pdf",
            page_number=1,
            text="Python is a great programming language.",
            metadata={"author": "Jane"}
        )
    ]
    
    # Add to store
    store.add_chunks(chunks)
    
    # Assert they are in the DB
    assert len(store.table.search().to_arrow()) == 2
    
    # Test semantic search
    results = store.search("What is a good programming language?", limit=1)
    assert len(results) == 1
    assert results[0].chunk_id == "chunk2"
    assert results[0].text == "Python is a great programming language."
    assert results[0].metadata["author"] == "Jane"
    
    results2 = store.search("Tell me about France.", limit=1)
    assert results2[0].chunk_id == "chunk1"

def test_delete_document():
    store = VectorStore(table_name="test_delete")
    
    chunks = [
        DocumentChunk(
            chunk_id="chunk1",
            document_path="test.pdf",
            page_number=1,
            text="Some text 1",
        ),
        DocumentChunk(
            chunk_id="chunk2",
            document_path="test.pdf",
            page_number=2,
            text="Some text 2",
        ),
        DocumentChunk(
            chunk_id="chunk3",
            document_path="other.pdf",
            page_number=1,
            text="Some text 3",
        )
    ]
    store.add_chunks(chunks)
    assert len(store.table.search().to_arrow()) == 3
    
    # Delete test.pdf
    store.delete_document("test.pdf")
    
    # Assert only other.pdf is left
    remaining = store.table.search().to_pydantic(ChunkRecord)
    assert len(remaining) == 1
    assert remaining[0].chunk_id == "chunk3"
    
