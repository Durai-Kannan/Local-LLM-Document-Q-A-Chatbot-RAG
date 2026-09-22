import os
import fitz  # PyMuPDF
import docx
from typing import List, Dict, Any
from app.core.logging_config import logger

class DocumentPage:
    def __init__(self, text: str, page_number: int, source_path: str, file_name: str):
        self.text = text
        self.page_number = page_number
        self.source_path = source_path
        self.file_name = file_name

class DocumentLoader:
    def load(self, file_path: str) -> List[DocumentPage]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()

        logger.info(f"Loading document: {file_name} (type: {ext})")

        if ext == ".pdf":
            return self._load_pdf(file_path, file_name)
        elif ext == ".docx":
            return self._load_docx(file_path, file_name)
        elif ext in [".txt", ".md"]:
            return self._load_text(file_path, file_name)
        else:
            raise ValueError(f"Unsupported file type: '{ext}'. Supported types: .pdf, .docx, .txt, .md")

    def _load_pdf(self, file_path: str, file_name: str) -> List[DocumentPage]:
        pages = []
        doc = fitz.open(file_path)
        for page_idx in range(len(doc)):
            page = doc.load_page(page_idx)
            text = page.get_text()
            if text.strip():
                pages.append(DocumentPage(
                    text=text.strip(),
                    page_number=page_idx + 1,
                    source_path=file_path,
                    file_name=file_name
                ))
        doc.close()
        logger.info(f"Extracted {len(pages)} non-empty pages from PDF: {file_name}")
        return pages

    def _load_docx(self, file_path: str, file_name: str) -> List[DocumentPage]:
        doc = docx.Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        if not full_text:
            return []
        return [DocumentPage(
            text=full_text,
            page_number=1,
            source_path=file_path,
            file_name=file_name
        )]

    def _load_text(self, file_path: str, file_name: str) -> List[DocumentPage]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read().strip()
        if not text:
            return []
        return [DocumentPage(
            text=text,
            page_number=1,
            source_path=file_path,
            file_name=file_name
        )]
