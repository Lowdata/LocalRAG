from typing import IO
from app.services.parser_service import ParserService
from app.services.chunk_service import ChunkService
from app.storage.vector_store import VectorStore
import os


class IngestionService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    from typing import Any
    def ingest_file(self, filename: str, content: IO[bytes]) -> dict[str, Any]:
        """
        Orchestrates the ingestion of a single file:
        1. Parses the file into plain text pages.
        2. Chunks the text into semantic/character chunks.
        3. Saves to LanceDB with embeddings.
        """
        ext = os.path.splitext(filename)[1].lower()

        # 1. Parse
        if ext == ".pdf":
            parsed_doc = ParserService.parse_pdf(filename, content)
        elif ext in [".html", ".htm"]:
            parsed_doc = ParserService.parse_html(filename, content)
        elif ext in [".md", ".markdown"]:
            parsed_doc = ParserService.parse_markdown(filename, content)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        # 2. Chunk
        chunks = ChunkService.chunk_document(parsed_doc)

        # 3. Store (which embeds automatically)
        # Delete existing chunks for this document to ensure idempotency
        self.vector_store.delete_document(filename)
        self.vector_store.add_chunks(chunks)

        return {
            "document_path": parsed_doc.document_path,
            "num_pages": len(parsed_doc.pages),
            "num_chunks": len(chunks),
        }
