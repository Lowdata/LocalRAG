import pytest
import io
from app.services.parser_service import ParserService

def test_parse_markdown() -> None:
    content = b"# Test Markdown\n\nThis is a **test**."
    stream = io.BytesIO(content)
    parsed = ParserService.parse_markdown("docs/test.md", stream)
    
    assert parsed.document_path == "docs/test.md"
    assert len(parsed.pages) == 1
    assert parsed.pages[0].page_number == 1
    
    # Assert Markdown is stripped
    assert "Test Markdown" in parsed.pages[0].text
    assert "This is a test." in parsed.pages[0].text
    assert "**" not in parsed.pages[0].text
    
    # Assert Metadata
    assert parsed.metadata["document_name"] == "test.md"
    assert parsed.metadata["file_type"] == "markdown"
    assert parsed.pages[0].metadata["document_name"] == "test.md"

def test_parse_html() -> None:
    content = b"<html><body><h1>Title</h1><p>HTML Test</p></body></html>"
    stream = io.BytesIO(content)
    parsed = ParserService.parse_html("pages/test.html", stream)
    
    assert parsed.document_path == "pages/test.html"
    assert len(parsed.pages) == 1
    assert "HTML Test" in parsed.pages[0].text
    assert parsed.metadata["file_type"] == "html"
