from pydantic import BaseModel
from typing import List, Dict, Any

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
