import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import markdown
from typing import IO
from app.schemas.document import ParsedDocument, ParsedPage


class ParserService:
    @staticmethod
    def parse_pdf(file_path: str, stream: IO[bytes]) -> ParsedDocument:
        doc = fitz.open(stream=stream.read(), filetype="pdf")
        pages = []
        page_count = len(doc)
        document_name = file_path.split("/")[-1]

        doc_metadata = {
            "document_name": document_name,
            "source_path": file_path,
            "file_type": "pdf",
            "page_count": page_count,
        }

        for i in range(page_count):
            page = doc.load_page(i)
            text = page.get_text("text")
            page_metadata = {"page_number": i + 1, **doc_metadata}
            pages.append(
                ParsedPage(page_number=i + 1, text=text, metadata=page_metadata)
            )

        return ParsedDocument(
            document_path=file_path, pages=pages, metadata=doc_metadata
        )

    @staticmethod
    def _clean_html_text(soup: BeautifulSoup) -> str:
        for block in soup.find_all(
            ["p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "li", "blockquote"]
        ):
            block.append("\n")
        text = soup.get_text(separator="")
        return "\n".join([line.strip() for line in text.split("\n") if line.strip()])

    @staticmethod
    def parse_html(file_path: str, stream: IO[bytes]) -> ParsedDocument:
        content = stream.read().decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")
        text = ParserService._clean_html_text(soup)

        document_name = file_path.split("/")[-1]
        metadata = {
            "document_name": document_name,
            "source_path": file_path,
            "file_type": "html",
            "page_count": 1,
        }

        pages = [
            ParsedPage(
                page_number=1, text=text, metadata={"page_number": 1, **metadata}
            )
        ]
        return ParsedDocument(document_path=file_path, pages=pages, metadata=metadata)

    @staticmethod
    def parse_markdown(file_path: str, stream: IO[bytes]) -> ParsedDocument:
        content = stream.read().decode("utf-8")
        html_content = markdown.markdown(content)
        soup = BeautifulSoup(html_content, "html.parser")
        text = ParserService._clean_html_text(soup)

        document_name = file_path.split("/")[-1]
        metadata = {
            "document_name": document_name,
            "source_path": file_path,
            "file_type": "markdown",
            "page_count": 1,
        }

        pages = [
            ParsedPage(
                page_number=1, text=text, metadata={"page_number": 1, **metadata}
            )
        ]
        return ParsedDocument(document_path=file_path, pages=pages, metadata=metadata)
