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
