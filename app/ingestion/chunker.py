import re
from typing import List, Dict, Any
from app.ingestion.loader import DocumentPage
from app.core.logging_config import logger

class Chunk:
    def __init__(self, chunk_id: str, document_id: str, file_name: str, text: str, page_number: int, chunk_index: int, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.file_name = file_name
        self.text = text
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.metadata = metadata

class TextChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        # Normalize whitespace while maintaining paragraph breaks
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def split_pages(self, pages: List[DocumentPage], document_id: str) -> List[Chunk]:
        chunks: List[Chunk] = []
        global_chunk_idx = 0

        for page in pages:
            cleaned_text = self.clean_text(page.text)
            if not cleaned_text:
                continue

            page_chunks_text = self._recursive_split(cleaned_text)

            for chunk_text in page_chunks_text:
                chunk_id = f"{document_id}_chunk_{global_chunk_idx:04d}"
                metadata = {
                    "document_id": document_id,
                    "file_name": page.file_name,
                    "page_number": page.page_number,
                    "chunk_id": chunk_id,
                    "chunk_index": global_chunk_idx,
                    "source_path": page.source_path
                }
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    file_name=page.file_name,
                    text=chunk_text,
                    page_number=page.page_number,
                    chunk_index=global_chunk_idx,
                    metadata=metadata
                ))
                global_chunk_idx += 1

        logger.info(f"Split document {document_id} into {len(chunks)} chunks (size: {self.chunk_size}, overlap: {self.chunk_overlap})")
        return chunks

    def _recursive_split(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        separators = ["\n\n", "\n", ". ", " ", ""]
        result_chunks = []
        
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            if end < text_len:
                # Try to find a natural break point backwards from end
                best_break = -1
                for sep in separators[:-1]:
                    pos = text.rfind(sep, start + self.chunk_overlap, end)
                    if pos != -1:
                        best_break = pos + len(sep)
                        break
                if best_break != -1:
                    end = best_break

            chunk_str = text[start:end].strip()
            if chunk_str:
                result_chunks.append(chunk_str)

            if end >= text_len:
                break

            # Move start forward with overlap
            start = max(start + 1, end - self.chunk_overlap)

        return result_chunks
