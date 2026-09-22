from typing import List, Dict, Any
from app.vectorstore.chroma_store import ChromaVectorStore
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.core.logging_config import logger

class DocumentService:
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.pipeline = DocumentIngestionPipeline(vector_store=vector_store)

    def upload_document(self, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        return self.pipeline.process_file(file_name, file_bytes)

    def list_documents(self) -> List[Dict[str, Any]]:
        return self.vector_store.get_all_documents()

    def delete_document(self, document_id: str) -> bool:
        return self.vector_store.delete_document(document_id)
