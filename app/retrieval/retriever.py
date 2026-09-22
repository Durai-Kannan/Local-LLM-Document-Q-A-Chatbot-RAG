from typing import List, Dict, Any, Tuple
from app.embeddings.embedding_model import LocalEmbeddingModel
from app.vectorstore.chroma_store import ChromaVectorStore
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.chat import SourceReference

class DocumentRetriever:
    def __init__(self, vector_store: ChromaVectorStore):
        self.embedding_model = LocalEmbeddingModel()
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = None, score_threshold: float = None) -> Tuple[List[Dict[str, Any]], List[SourceReference]]:
        effective_top_k = top_k if top_k is not None else settings.TOP_K
        effective_threshold = score_threshold if score_threshold is not None else settings.SCORE_THRESHOLD

        logger.info(f"Retrieving top {effective_top_k} chunks for query: '{query}' (threshold={effective_threshold})")

        query_embedding = self.embedding_model.encode_single(query)
        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=effective_top_k,
            score_threshold=effective_threshold
        )

        sources: List[SourceReference] = []
        seen_chunks = set()

        for chunk in retrieved_chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id in seen_chunks:
                continue
            seen_chunks.add(chunk_id)

            metadata = chunk.get("metadata", {})
            file_name = metadata.get("file_name", "Unknown Document")
            page_number = metadata.get("page_number")
            text_snippet = chunk.get("text", "")[:150] + "..." if len(chunk.get("text", "")) > 150 else chunk.get("text", "")

            sources.append(SourceReference(
                document=file_name,
                page=page_number,
                chunk_id=chunk_id,
                relevance_score=chunk.get("similarity"),
                snippet=text_snippet
            ))

        return retrieved_chunks, sources
