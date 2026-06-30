import hashlib

def generate_chunk_hash(document_path: str, page_number: int, chunk_text: str) -> str:
    """Generates a SHA256 hash for idempotent chunk ingestion."""
    content = f"{document_path}{page_number}{chunk_text}".encode("utf-8")
    return hashlib.sha256(content).hexdigest()
