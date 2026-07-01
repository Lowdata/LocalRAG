from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IngestResponse(BaseModel):
    message: str
    document_path: str
    num_pages: int
    num_chunks: int

class DocumentInfo(BaseModel):
    document_path: str
    num_chunks: int
    metadata: Dict[str, Any]

class DocumentsListResponse(BaseModel):
    documents: List[DocumentInfo]

class DeleteResponse(BaseModel):
    message: str
    document_path: str


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    document_path: Optional[str] = None

class SourceChunk(BaseModel):
    chunk_id: str
    document_path: str
    page_number: int
    text: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
