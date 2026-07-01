from app.schemas.document import ParsedDocument, ParsedPage
from app.services.chunk_service import ChunkService

def test_chunker():
    with open("README.md", "r") as f:
        text = f.read()
        
    doc = ParsedDocument(
        document_path="README.md",
        pages=[ParsedPage(page_number=1, text=text, metadata={})]
    )
    
    chunks = ChunkService.chunk_document(doc, chunk_size=500, chunk_overlap=50)
    for i, c in enumerate(chunks):
        print(f"\n--- Chunk {i} ---")
        print(repr(c.text[:30]))

if __name__ == "__main__":
    test_chunker()
