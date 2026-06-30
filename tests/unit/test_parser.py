import pytest
import io
from app.services.parser_service import ParserService

def test_parse_markdown() -> None:
    content = b"# Test Markdown\n\nThis is a test."
    stream = io.BytesIO(content)
    parsed = ParserService.parse_markdown("test.md", stream)
    
    assert parsed.document_path == "test.md"
    assert len(parsed.pages) == 1
    assert parsed.pages[0].page_number == 1
    assert "This is a test." in parsed.pages[0].text

def test_parse_html() -> None:
    content = b"<html><body><h1>Title</h1><p>HTML Test</p></body></html>"
    stream = io.BytesIO(content)
    parsed = ParserService.parse_html("test.html", stream)
    
    assert parsed.document_path == "test.html"
    assert len(parsed.pages) == 1
    assert "HTML Test" in parsed.pages[0].text
