import os
import hashlib
import datetime
import uuid
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.ingestion.loader import DocumentLoader
from app.ingestion.chunker import TextChunker
from app.embeddings.embedding_model import LocalEmbeddingModel
from app.vectorstore.chroma_store import ChromaVectorStore

class DocumentIngestionPipeline:
    def __init__(self, vector_store: ChromaVectorStore):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        self.embedding_model = LocalEmbeddingModel()
        self.vector_store = vector_store

    def calculate_file_hash(self, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def process_file(self, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        file_hash = self.calculate_file_hash(file_bytes)
        file_size = len(file_bytes)

        # Check for duplicates by hash in vectorstore
        existing_docs = self.vector_store.get_all_documents()
        for doc in existing_docs:
            if doc.get("file_hash") == file_hash or (doc.get("file_name") == file_name and doc.get("file_size") == file_size):
                logger.info(f"Document '{file_name}' already ingested (matching hash/size). Skipping duplicate.")
                return {
                    "status": "already_exists",
                    "document_id": doc["document_id"],
                    "file_name": file_name,
                    "total_chunks": doc.get("total_chunks", 0),
                    "message": f"Document '{file_name}' is already ingested."
                }

        document_id = f"doc_{uuid.uuid4().hex[:8]}"
        save_path = os.path.join(settings.DOCUMENTS_PATH, f"{document_id}_{file_name}")

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        logger.info(f"Saved document to disk: {save_path}")

        # 1. Load document pages
        pages = self.loader.load(save_path)
        if not pages:
            os.remove(save_path)
            raise ValueError(f"No readable text content found in '{file_name}'.")

        # 2. Chunk text
        chunks = self.chunker.split_pages(pages, document_id=document_id)

        # Attach document metadata to each chunk
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        file_type = os.path.splitext(file_name)[1].lower()
        
        for chunk in chunks:
            chunk.metadata.update({
                "file_size": file_size,
                "file_hash": file_hash,
                "file_type": file_type,
                "created_at": created_at,
                "total_pages": len(pages)
            })

        # 3. Generate embeddings
        chunk_texts = [c.text for c in chunks]
        embeddings = self.embedding_model.encode(chunk_texts)

        # 4. Store in ChromaDB
        self.vector_store.add_chunks(chunks, embeddings)

        return {
            "status": "success",
            "document_id": document_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "created_at": created_at
        }
