from app.utils.hashing import generate_chunk_hash

def test_generate_chunk_hash() -> None:
    doc_path = "test.pdf"
    page_num = 1
    text = "Hello world"
    hash1 = generate_chunk_hash(doc_path, page_num, text)
    hash2 = generate_chunk_hash(doc_path, page_num, text)
    hash3 = generate_chunk_hash(doc_path, 2, text)
    
    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64  # SHA256 length
