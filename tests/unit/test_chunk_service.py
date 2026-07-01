from app.schemas.document import ParsedDocument, ParsedPage
from app.services.chunk_service import ChunkService


def test_chunk_document_basic() -> None:
    # Create a dummy ParsedDocument
    page = ParsedPage(page_number=1, text="A" * 1000, metadata={"source": "test"})
    doc = ParsedDocument(
        document_path="test.pdf", pages=[page], metadata={"type": "pdf"}
    )

    # Chunk with size 100, overlap 20
    chunks = ChunkService.chunk_document(doc, chunk_size=100, chunk_overlap=20)

    assert len(chunks) > 0
    # First chunk should be exactly 100 characters
    assert len(chunks[0].text) == 100

    # Check that metadata is preserved
    assert chunks[0].metadata == {"source": "test"}
    assert chunks[0].document_path == "test.pdf"
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_id is not None


def test_chunk_document_overlap_and_break() -> None:
    # Create text with spaces to test breakpoint logic
    text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10"
    page = ParsedPage(page_number=1, text=text)
    doc = ParsedDocument(document_path="test.txt", pages=[page])

    # Chunk with small size to force breaking
    chunks = ChunkService.chunk_document(doc, chunk_size=25, chunk_overlap=10)

    # Assert we got chunks
    assert len(chunks) > 0
    # Verify no chunks are over chunk_size
    for chunk in chunks:
        assert len(chunk.text) <= 25

    # Check that it breaks cleanly on spaces where possible
    assert not chunks[0].text.endswith("Wor")
