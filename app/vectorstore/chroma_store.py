import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.ingestion.chunker import Chunk

class ChromaVectorStore:
    def __init__(self):
        logger.info(f"Initializing ChromaDB client at: '{settings.CHROMA_PATH}'")
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]):
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Added {len(chunks)} chunks to ChromaDB knowledge_base collection.")

    def search(self, query_embedding: List[float], top_k: int = 5, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return retrieved

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, doc_text, metadata, distance in zip(ids, documents, metadatas, distances):
            # Cosine distance in Chroma: similarity = 1.0 - distance
            similarity = round(1.0 - float(distance), 4)

            if score_threshold is not None and similarity < score_threshold:
                logger.debug(f"Chunk {chunk_id} filtered out (similarity {similarity} < threshold {score_threshold})")
                continue

            retrieved.append({
                "chunk_id": chunk_id,
                "text": doc_text,
                "metadata": metadata,
                "similarity": similarity,
                "distance": distance
            })

        logger.info(f"Retrieved {len(retrieved)} relevant chunks from ChromaDB (top_k={top_k}).")
        return retrieved

    def get_all_documents(self) -> List[Dict[str, Any]]:
        all_items = self.collection.get(include=["metadatas"])
        if not all_items or not all_items.get("metadatas"):
            return []

        doc_summary: Dict[str, Dict[str, Any]] = {}
        for meta in all_items["metadatas"]:
            doc_id = meta.get("document_id")
            if not doc_id:
                continue

            if doc_id not in doc_summary:
                doc_summary[doc_id] = {
                    "document_id": doc_id,
                    "file_name": meta.get("file_name", "Unknown"),
                    "file_type": meta.get("file_name", "").split(".")[-1] if "." in meta.get("file_name", "") else "unknown",
                    "file_size": meta.get("file_size", 0),
                    "created_at": meta.get("created_at", ""),
                    "total_chunks": 0
                }
            doc_summary[doc_id]["total_chunks"] += 1

        return list(doc_summary.values())

    def delete_document(self, document_id: str) -> bool:
        items = self.collection.get(where={"document_id": document_id})
        if items and items.get("ids"):
            self.collection.delete(ids=items["ids"])
            logger.info(f"Deleted {len(items['ids'])} chunks for document_id: '{document_id}' from ChromaDB.")
            return True
        return False

    def count_chunks(self) -> int:
        return self.collection.count()
