# Development Log

## Milestone 1
**Date:** 2026-07-01
**Objective:** Project scaffold and foundation setup.
**Completed Tasks:** Setup directories, config, logging, Docker, setup scripts, and health endpoint.
**Files Added:** `pyproject.toml`, `app/main.py`, `app/core/config.py`, `app/middleware/logging.py`, `Dockerfile`, `docker-compose.yml`, setup scripts, etc.
**Files Modified:** N/A
**Classes Added:** `Settings`
**Functions Added:** `log_requests`, `health_check`
**Endpoints Added:** `GET /health`
**Tests Added:** N/A
**Configuration Changes:** Added Pydantic Settings and standard Loguru logging.
**Architectural Decisions:** 
- Used Pydantic v2 for configuration management.
- Loguru for centralized request logging as middleware.
- Only backend is dockerized.
**Tradeoffs:** Simple middleware logging is used rather than complex APM tools for simplicity and speed.
**Known Issues:** None yet.
**Future Improvements:** Add detailed token and retrieval logging within the specific services (to be done in later phases).
**Next Milestone:** Phase 2: Document Parsing & Hashing

## Milestone 2
**Date:** 2026-07-01
**Objective:** Document Parsing & Hashing
**Completed Tasks:** Implemented PDF, HTML, and Markdown parsers. Implemented SHA256 chunk hashing. Added dummy files.
**Files Added:** `app/schemas/document.py`, `app/utils/hashing.py`, `app/services/parser_service.py`, `tests/unit/test_parser.py`, `tests/unit/test_hashing.py`, `docs/records.md`
**Files Modified:** `task.md`
**Classes Added:** `ParsedPage`, `ParsedDocument`, `ParserService`
**Functions Added:** `generate_chunk_hash`, `parse_pdf`, `parse_html`, `parse_markdown`
**Endpoints Added:** N/A
**Tests Added:** `test_generate_chunk_hash`, `test_parse_markdown`, `test_parse_html`
**Configuration Changes:** N/A
**Architectural Decisions:** 
- Used PyMuPDF for fast PDF parsing and text extraction.
- BeautifulSoup4 for HTML.
- Kept schemas generic (`ParsedDocument`) to serve as a uniform input to the next phase (chunking).
**Tradeoffs:** Raw markdown extraction is used initially instead of parsing markdown AST, as semantic chunking will be handled downstream if needed.
**Known Issues:** None.
**Future Improvements:** Handle complex tables in PDFs.
**Next Milestone:** Phase 3: Custom Chunker

# Milestone 3
Date: 2026-07-01
Objective: Build a custom text chunking utility from scratch.
Completed Tasks: Implemented an overlapping character chunker that preserves document metadata, sets deterministic chunk IDs using SHA256 hashes, and handles boundaries properly. Configured via .env.
Files Added:
- app/services/chunk_service.py
- tests/unit/test_chunk_service.py
Files Modified:
- app/core/config.py
- app/schemas/document.py
Classes Added: ChunkService, DocumentChunk
Functions Added: ChunkService.chunk_document
Endpoints Added: None
Tests Added: test_chunk_document_basic, test_chunk_document_overlap_and_break
Configuration Changes: Added chunk_size and chunk_overlap to app/core/config.py.
Architectural Decisions: Avoided LangChain splitters entirely, implementing an independent text chunker.
Tradeoffs: A character chunker is simple and fast, but lacks semantic understanding compared to an NLP-based sentence chunker.
Known Issues: None.
Future Improvements: Could implement semantic recursive chunking if retrieval quality isn't high enough.
Next Milestone: Phase 4 (Embeddings)

# Milestone 4
Date: 2026-07-01
Objective: Implement a purely local text embedding service.
Completed Tasks: Integrated `SentenceTransformers` using `BAAI/bge-small-en-v1.5` (384 dimensions). Added unit tests to automatically pull the model cache and verify operations.
Files Added:
- app/services/embedding_service.py
- tests/unit/test_embedding_service.py
Files Modified:
- app/core/config.py
Classes Added: EmbeddingService
Functions Added: EmbeddingService.get_embedding, EmbeddingService.get_embeddings
Endpoints Added: None
Tests Added: test_get_embedding, test_get_embeddings
Configuration Changes: Added embedding_model to config.
Architectural Decisions: Used lazy loading (`cls._get_model()`) to avoid loading PyTorch overhead on startup unless an embedding is strictly needed. Kept the model completely localized via standard HuggingFace Cache.
Tradeoffs: The first API call takes extra time to load the model into memory.
Known Issues: None.
Future Improvements: Could batch encode at the router layer instead of individual encode calls if throughput is a bottleneck.
Next Milestone: Phase 5 (Vector Database / LanceDB)
