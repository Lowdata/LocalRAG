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
