# Work Records

## Phase 1: Project Scaffold & Foundation
**What:** Initialized project structure, dependencies, logging middleware, Docker setup, CI/CD, and basic scripts.
**How:** Created all required directories. Wrote pyproject.toml with FastAPI, Uvicorn, and other deps. Added Loguru for middleware logging. Added Dockerfile and docker-compose.yml for backend.
**Where (Filenames):** 
- `pyproject.toml`
- `app/main.py`
- `app/core/config.py`
- `app/middleware/logging.py`
- `Dockerfile`, `docker-compose.yml`
- `.github/workflows/ci.yml`
- `scripts/setup.*`, `scripts/run.*`
- `tests/unit/test_main.py`
- `docs/development_log.md`, `docs/adr/*`

## Phase 2: Document Parsing & Hashing (In Progress)
**What:** Implemented the hashing utility and document schemas, as well as the initial PDF, HTML, and Markdown parsers.
**How:** Created Pydantic models for `ParsedDocument` and `ParsedPage`. Used `hashlib.sha256` for the hashing utility based on `document_path + page_number + chunk_text`. Used `fitz` (PyMuPDF) and `BeautifulSoup` for parsing in `ParserService`.
**Where (Filenames):**
- `app/schemas/document.py`
- `app/utils/hashing.py`
- `app/services/parser_service.py`

## Phase 2: Refinements
**What:** Improved markdown parsing to plain text and added rich metadata extraction for PDFs/HTML/Markdown.
**How:** Used `markdown` and `BeautifulSoup4` combined to strip markdown syntax and convert it to plain text. Extracted `document_name`, `page_number`, `page_count`, `source_path`, and `file_type` in the parsers and injected them into the document/page metadata payload.
**Where (Filenames):** 
- `app/services/parser_service.py`
- `tests/unit/test_parser.py`

## Docker Fixes & Documentation
**What:** Fixed Docker configuration and updated README.
**How:** 
1. Added `.env` file via `.env.example`.
2. Changed `Dockerfile` to `COPY . .` before `RUN pip install .` to fix missing package directory error.
3. Added `README.md` with explicit local vs docker run instructions and a note about the initial PyTorch download time.
**Where (Filenames):**
- `.env`
- `Dockerfile`
- `README.md`

## Phase 3: Custom Chunker
**What:** Implemented a custom overlapping character-based chunking service to split ParsedDocuments into DocumentChunks without losing context.
**How:** 
1. Added `chunk_size=500` and `chunk_overlap=50` to `app/core/config.py` (overridable via `.env`).
2. Added `DocumentChunk` schema to `app/schemas/document.py`.
3. Created `ChunkService` in `app/services/chunk_service.py` that loops through page text, slices by `chunk_size`, and steps forward by `chunk_size - chunk_overlap`, trying to intelligently break on spaces or newlines.
4. Used `generate_chunk_hash` for deterministic chunk IDs.
5. Wrote Pytest tests to verify boundaries and metadata copying.
**Where (Filenames):**
- `app/core/config.py`
- `app/schemas/document.py`
- `app/services/chunk_service.py`
- `tests/unit/test_chunk_service.py`

## Phase 4: Embeddings
**What:** Implemented the Embedding service using `sentence-transformers` and the local model `BAAI/bge-small-en-v1.5`.
**How:** 
1. Added `embedding_model` setting to `app/core/config.py`.
2. Created `app/services/embedding_service.py` featuring lazy loading of the model so importing it doesn't cause immediate delays, and returning lists of floats (384 dimensions).
3. Created unit tests in `tests/unit/test_embedding_service.py` to trigger model download and verify dimensions.
**Where (Filenames):**
- `app/core/config.py`
- `app/services/embedding_service.py`
- `tests/unit/test_embedding_service.py`

## Patch: Parser Service Inline Element Fix
**What:** Fixed a bug in `ParserService` where inline HTML elements (like `**bold**` markdown becoming `<strong>bold</strong>`) were being stripped into separate lines instead of kept adjacent to surrounding text.
**How:** 
1. Added a private `_clean_html_text` method in `ParserService`.
2. It iterates through all block-level tags (`p`, `h1`, `div`, `li`, etc.) and manually appends a `\n` to them.
3. Then it runs `soup.get_text(separator="")` so inline tags seamlessly merge with surrounding text without breaking into newlines.
**Where (Filenames):**
- `app/services/parser_service.py`

## Phase 5: Vector Database (LanceDB)
**What:** Implemented  using local LanceDB to persist chunks and their embeddings.
**How:** 
1. Defined  schema using  with a  field.
2. Created  providing , , and  functionality.
3. Automatically maps Pydantic metadata dicts to JSON strings for compatibility with the underlying PyArrow schema.
4. Created  to ensure chunk insertion, semantic search, and document deletion work seamlessly against a temporary DB.
**Where (Filenames):**
- 
- 
- 

## Phase 5: Vector Database (LanceDB)
**What:** Implemented `VectorStore` using local LanceDB to persist chunks and their embeddings.
**How:** 
1. Defined `ChunkRecord` schema using `lancedb.pydantic.LanceModel` with a `Vector(384)` field.
2. Created `app/storage/vector_store.py` providing `add_chunks`, `search`, and `delete_document` functionality.
3. Automatically maps Pydantic metadata dicts to JSON strings for compatibility with the underlying PyArrow schema.
4. Created `tests/unit/test_vector_store.py` to ensure chunk insertion, semantic search, and document deletion work seamlessly against a temporary DB.
**Where (Filenames):**
- `app/schemas/vector.py`
- `app/storage/vector_store.py`
- `tests/unit/test_vector_store.py`

## Phase 6: Storage API
**What:** Created FastAPI endpoints to upload files, chunk them, embed them, and store them into LanceDB. Also added document listing and deletion.
**How:** 
1. Added Pydantic API schemas in `app/schemas/api.py`.
2. Created `IngestionService` to orchestrate file parsing -> chunking -> vector storage.
3. Created `app/api/endpoints/storage.py` with `/ingest`, `/documents`, and `DELETE /documents/{id}` routes.
4. Integrated `python-multipart` to support file uploads.
**Where (Filenames):**
- `app/schemas/api.py`
- `app/services/ingestion_service.py`
- `app/api/endpoints/storage.py`
- `app/main.py`
- `pyproject.toml`

## Phase 7: Retrieval & LLM (Ollama)
**What:** Implemented `LLMService` to talk to the local Ollama instance and created the `/query` endpoint for Retrieval-Augmented Generation.
**How:** 
1. Added Pydantic schemas (`QueryRequest`, `QueryResponse`, `SourceChunk`) in `app/schemas/api.py`.
2. Created `app/services/llm_service.py` to prompt the local Ollama LLM asynchronously using `httpx.AsyncClient`.
3. Built `app/api/endpoints/query.py` combining vector search and prompt generation.
4. Hooked it up in `app/main.py` under the `/api/v1/query` route.
5. Wrote integration tests Mocking the LLM in `tests/integration/test_query_api.py`.
**Where (Filenames):**
- `app/schemas/api.py`
- `app/services/llm_service.py`
- `app/api/endpoints/query.py`
- `app/main.py`
- `tests/integration/test_query_api.py`
