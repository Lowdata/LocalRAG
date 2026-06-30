from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ParsedPage(BaseModel):
    page_number: int
    text: str
    metadata: Dict[str, Any] = {}

class ParsedDocument(BaseModel):
    document_path: str
    pages: List[ParsedPage]
    metadata: Dict[str, Any] = {}
