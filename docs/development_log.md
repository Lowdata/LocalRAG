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

## Patch: Parser Service Inline Element Fix
Date: 2026-07-01
Objective: Fix markdown parser test failure caused by BeautifulSoup newline separation on inline elements.
Completed Tasks: Implemented `_clean_html_text` helper in `ParserService` to intelligently separate only block-level HTML elements and safely merge inline elements.
Files Modified:
- app/services/parser_service.py

# Milestone 5
Date: 2026-07-01
Objective: Configure local LanceDB in  and build storage layer.
Completed Tasks: Implemented  for LanceDB integration. Wrote unit tests for inserting, semantic search, and document deletion. Fully typed with mypy.
Files Added:
- app/schemas/vector.py
- app/storage/vector_store.py
- tests/unit/test_vector_store.py
Classes Added: ChunkRecord, VectorStore
Functions Added: VectorStore.add_chunks, VectorStore.search, VectorStore.delete_document
Endpoints Added: None
Tests Added: test_vector_store_add_and_search, test_delete_document
Configuration Changes: Utilizing vector_db_path from config.
Architectural Decisions: Used  for schema definition. Store metadata as JSON strings because native Arrow maps can be rigid with nested dicts.
Tradeoffs: Need to serialize/deserialize metadata to/from JSON strings manually via properties.
Known Issues: None.
Future Improvements: None.
Next Milestone: Phase 6 (Storage API)

# Milestone 5
Date: 2026-07-01
Objective: Configure local LanceDB in `data/lancedb/` and build storage layer.
Completed Tasks: Implemented `VectorStore` for LanceDB integration. Wrote unit tests for inserting, semantic search, and document deletion. Fully typed with mypy.
Files Added:
- app/schemas/vector.py
- app/storage/vector_store.py
- tests/unit/test_vector_store.py
Classes Added: ChunkRecord, VectorStore
Functions Added: VectorStore.add_chunks, VectorStore.search, VectorStore.delete_document
Endpoints Added: None
Tests Added: test_vector_store_add_and_search, test_delete_document
Configuration Changes: Utilizing vector_db_path from config.
Architectural Decisions: Used `lancedb.pydantic.LanceModel` for schema definition. Store metadata as JSON strings because native Arrow maps can be rigid with nested dicts.
Tradeoffs: Need to serialize/deserialize metadata to/from JSON strings manually via properties.
Known Issues: None.
Future Improvements: None.
Next Milestone: Phase 6 (Storage API)

# Milestone 6
Date: 2026-07-01
Objective: Build the API storage layer to ingest documents and manage them via FastAPI.
Completed Tasks: Implemented `/api/v1/ingest`, `/api/v1/documents`, and DELETE routes. Wired up the `IngestionService` which ties together the parser, chunker, and vector store perfectly. Added integration tests to verify file upload and parsing lifecycle.
Files Added/Modified:
- app/schemas/api.py
- app/services/ingestion_service.py
- app/api/endpoints/storage.py
- app/main.py
- pyproject.toml
Classes Added: IngestResponse, DocumentInfo, DocumentsListResponse, DeleteResponse, IngestionService
Functions Added: ingest_document, list_documents, delete_document
Endpoints Added: POST /api/v1/ingest, GET /api/v1/documents, DELETE /api/v1/documents/{document_path}
Tests Added: test_ingest_markdown, test_list_documents, test_delete_document
Configuration Changes: Added `python-multipart` to `pyproject.toml`.
Architectural Decisions: Implemented manual grouping of records in `list_documents` via Python since LanceDB Python API lacks complex SQL GROUP BY. This is perfectly performant for local RAG scales.
Tradeoffs: None
Known Issues: None.
Future Improvements: None.
Next Milestone: Phase 7 (Retrieval & LLM integration with Ollama)

# Milestone 7
Date: 2026-07-01
Objective: Build the Retrieval and LLM pipeline to answer queries utilizing Ollama.
Completed Tasks: Implemented `LLMService`, created the `POST /api/v1/query` endpoint, wired it to `VectorStore`, added mock tests to verify flow, and fully typed it.
Files Added/Modified:
- app/schemas/api.py
- app/services/llm_service.py
- app/api/endpoints/query.py
- app/main.py
- tests/integration/test_query_api.py
Classes Added: QueryRequest, QueryResponse, SourceChunk, LLMService
Functions Added: LLMService.generate_response, LLMService.build_prompt, query_documents
Endpoints Added: POST /api/v1/query
Tests Added: test_query_api
Configuration Changes: None.
Architectural Decisions: Used `httpx` to cleanly interface with Ollama REST API directly, rather than bringing in heavyweight SDKs like Langchain. 
Tradeoffs: Need to construct the RAG prompt manually.
Known Issues: None.
Future Improvements: Support streaming responses using Server-Sent Events (SSE).
Next Milestone: Phase 8 (Evaluation Pipeline)

# Milestone 8
Date: 2026-07-01
Objective: Build metrics and scripts/evaluate.py.
Completed Tasks: Created a standalone async evaluation script that pings the `POST /api/v1/query` endpoint.
Files Added/Modified:
- scripts/evaluate.py
Classes Added: None
Functions Added: run_evaluation, main
Endpoints Added: None
Tests Added: None (This script acts as the evaluation suite).
Configuration Changes: None.
Architectural Decisions: Used `asyncio` and `httpx.AsyncClient` to allow for scalable asynchronous benchmarking if the question dataset grows large.
Tradeoffs: Hardcoded dataset for simplicity right now, but easily expandable.
Known Issues: None.
Future Improvements: Support reading questions from a CSV/JSON file.
Next Milestone: Phase 9 (Documentation)

# Milestone 9
Date: 2026-07-01
Objective: Finalize architecture docs and README.md.
Completed Tasks: Updated `README.md` and added `docs/architecture.md`.
Files Added/Modified:
- README.md
- docs/architecture.md
Classes Added: None
Functions Added: None
Endpoints Added: None
Tests Added: None
Configuration Changes: None.
Architectural Decisions: Used Mermaid.js for architecture diagrams to render natively in GitHub and markdown viewers.
Tradeoffs: None
Known Issues: None.
Future Improvements: Provide detailed Swagger/OpenAPI examples.
Next Milestone: Project Completed.
