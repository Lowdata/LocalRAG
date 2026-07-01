from app.schemas.document import ParsedDocument, ParsedPage
from app.services.chunk_service import ChunkService


def test_chunking_boundaries():
    # A text with exactly 25 characters
    # "This is a test document."
    text = "This is a test document that should be chunked properly."
    doc = ParsedDocument(
        document_path="test.md",
        pages=[ParsedPage(page_number=1, text=text, metadata={})],
    )

    # Very small chunk size to force multiple overlapping chunks
    chunks = ChunkService.chunk_document(doc, chunk_size=20, chunk_overlap=10)

    print("\n--- Testing Chunk Boundaries ---")
    for i, c in enumerate(chunks):
        print(f"Chunk {i}: '{c.text}'")

    print("\n--- Chunk Test Passed ---")


if __name__ == "__main__":
    test_chunking_boundaries()
