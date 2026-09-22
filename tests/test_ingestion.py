import os
import pytest
from app.ingestion.loader import DocumentLoader, DocumentPage
from app.ingestion.chunker import TextChunker, Chunk

def test_text_chunker_basic():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    pages = [
        DocumentPage(
            text="This is page one of a test document that contains multiple sentences to test chunking.",
            page_number=1,
            source_path="/tmp/sample.txt",
            file_name="sample.txt"
        )
    ]
    chunks = chunker.split_pages(pages, document_id="test_doc_1")
    assert len(chunks) > 0
    assert isinstance(chunks[0], Chunk)
    assert chunks[0].document_id == "test_doc_1"
    assert chunks[0].page_number == 1

def test_document_loader_txt(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Line 1: Hello World\nLine 2: Testing RAG loader.", encoding="utf-8")
    
    loader = DocumentLoader()
    pages = loader.load(str(test_file))
    
    assert len(pages) == 1
    assert "Hello World" in pages[0].text
    assert pages[0].page_number == 1
