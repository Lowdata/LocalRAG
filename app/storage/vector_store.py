import lancedb
from typing import List, Optional
import json
import os
from app.core.config import settings
from app.schemas.vector import ChunkRecord
from app.schemas.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class VectorStore:
    def __init__(self, table_name: str = "chunks"):
        self.table_name = table_name

        # Ensure directory exists
        os.makedirs(settings.vector_db_path, exist_ok=True)

        # Connect to LanceDB
        self.db = lancedb.connect(settings.vector_db_path)

        try:
            self.table = self.db.open_table(self.table_name)
        except Exception:
            self.table = self.db.create_table(self.table_name, schema=ChunkRecord)

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Generates embeddings for chunks and inserts them into LanceDB."""
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        embeddings = EmbeddingService.get_embeddings(texts)

        records = []
        for i, chunk in enumerate(chunks):
            record = ChunkRecord(
                chunk_id=chunk.chunk_id,
                document_path=chunk.document_path,
                page_number=chunk.page_number,
                text=chunk.text,
                vector=embeddings[i],
                metadata_json=json.dumps(chunk.metadata),
            )
            records.append(record)

        self.table.add(records)

    def search(
        self, query: str, limit: int = 5, document_path: Optional[str] = None
    ) -> List[ChunkRecord]:
        """Embeds the query and searches LanceDB for nearest neighbors."""
        query_embedding = EmbeddingService.get_embedding(query)

        # search returns a builder
        builder = self.table.search(query_embedding).limit(limit)

        # Apply metadata filtering if requested
        if document_path:
            safe_path = document_path.replace("'", "''")
            builder = builder.where(f"document_path = '{safe_path}'", prefilter=True)

        results = builder.to_pydantic(ChunkRecord)
        return results  # type: ignore

    def delete_document(self, document_path: str) -> None:
        """Deletes all chunks associated with a document."""
        # We need to escape single quotes if the document_path has them
        safe_path = document_path.replace("'", "''")
        self.table.delete(f"document_path = '{safe_path}'")

    def count_total_vectors(self) -> int:
        """Returns the total number of vectors currently in the database."""
        return len(self.table)
