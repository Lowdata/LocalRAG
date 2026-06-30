import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from typing import List, IO
from app.schemas.document import ParsedDocument, ParsedPage

class ParserService:
    @staticmethod
    def parse_pdf(file_path: str, stream: IO[bytes]) -> ParsedDocument:
        doc = fitz.open(stream=stream.read(), filetype="pdf")
        pages = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text("text")
            pages.append(ParsedPage(page_number=i+1, text=text))
        return ParsedDocument(document_path=file_path, pages=pages)

    @staticmethod
    def parse_html(file_path: str, stream: IO[bytes]) -> ParsedDocument:
        content = stream.read().decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        pages = [ParsedPage(page_number=1, text=text)]
        return ParsedDocument(document_path=file_path, pages=pages)

    @staticmethod
    def parse_markdown(file_path: str, stream: IO[bytes]) -> ParsedDocument:
        # For markdown, we can just extract the raw text for now.
        content = stream.read().decode("utf-8")
        pages = [ParsedPage(page_number=1, text=content)]
        return ParsedDocument(document_path=file_path, pages=pages)
