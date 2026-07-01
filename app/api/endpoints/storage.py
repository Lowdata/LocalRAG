from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict
from app.schemas.api import (
    IngestResponse,
    DocumentsListResponse,
    DocumentInfo,
    DeleteResponse,
)
from app.storage.vector_store import VectorStore
from app.services.ingestion_service import IngestionService
import io

router = APIRouter()


# Dependency to get vector store (allows easy mocking in tests)
def get_vector_store() -> VectorStore:
    return VectorStore()


def get_ingestion_service(
    store: VectorStore = Depends(get_vector_store),
) -> IngestionService:
    return IngestionService(store)


from typing import Any
@router.post("/ingest", response_model=IngestResponse)
@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> Any:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content = await file.read()
    stream = io.BytesIO(content)

    try:
        result = ingestion_service.ingest_file(file.filename, stream)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal error during ingestion: {str(e)}"
        )

    return IngestResponse(
        message="Document ingested successfully",
        document_path=result["document_path"],
        num_pages=result["num_pages"],
        num_chunks=result["num_chunks"],
    )


@router.get("/documents", response_model=DocumentsListResponse)
async def list_documents(store: VectorStore = Depends(get_vector_store)) -> Any:
    try:
        # Group chunks by document_path
        # LanceDB doesn't have complex GROUP BY yet in the Python API easily without DuckDB,
        # so we will pull all document_path and metadata and aggregate in python.
        # For a massive DB, this wouldn't scale, but for local RAG it's fine.
        records = (
            store.table.search()
            .select(["document_path", "metadata_json"])
            .to_arrow()
            .to_pylist()
        )

        import json

        doc_map: Dict[str, DocumentInfo] = {}
        for r in records:
            path = r["document_path"]
            if path not in doc_map:
                doc_map[path] = DocumentInfo(
                    document_path=path,
                    num_chunks=1,
                    metadata=json.loads(r["metadata_json"]),
                )
            else:
                doc_map[path].num_chunks += 1

        return DocumentsListResponse(documents=list(doc_map.values()))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing documents: {str(e)}"
        )


@router.delete("/documents/{document_path:path}", response_model=DeleteResponse)
async def delete_document(
    document_path: str, store: VectorStore = Depends(get_vector_store)
) -> Any:
    try:
        store.delete_document(document_path)
        return DeleteResponse(
            message="Document deleted successfully", document_path=document_path
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}"
        )
