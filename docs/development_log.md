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
