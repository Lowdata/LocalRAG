from typing import Dict, Any
from lancedb.pydantic import LanceModel, Vector
import json


class ChunkRecord(LanceModel):  # type: ignore
    chunk_id: str
    document_path: str
    page_number: int
    text: str
    # 384 is the dimension for BAAI/bge-small-en-v1.5
    vector: Vector(384)  # type: ignore

    # Store metadata as a JSON string since dicts can be tricky in Arrow schemas
    metadata_json: str

    @property
    def metadata(self) -> Dict[str, Any]:
        return json.loads(self.metadata_json)  # type: ignore
