import pytest
from app.embeddings.embedding_model import LocalEmbeddingModel
from app.vectorstore.chroma_store import ChromaVectorStore
from app.ingestion.chunker import Chunk

def test_embedding_model():
    model = LocalEmbeddingModel()
    texts = ["Retrieval Augmented Generation", "Local LLM testing"]
    embeddings = model.encode(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384  # all-MiniLM-L6-v2 vector dimension

def test_chroma_store_add_and_search(tmp_path):
    os_chroma_path = str(tmp_path / "chroma_test")
    from app.core.config import settings
    original_path = settings.CHROMA_PATH
    settings.CHROMA_PATH = os_chroma_path

    try:
        store = ChromaVectorStore()
        model = LocalEmbeddingModel()
        
        meta1 = {"document_id": "doc_1", "file_name": "python.txt", "page_number": 1}
        chunk1 = Chunk(
            chunk_id="chk_1",
            document_id="doc_1",
            file_name="python.txt",
            text="Python is a dynamic programming language.",
            page_number=1,
            chunk_index=0,
            metadata=meta1
        )
        meta2 = {"document_id": "doc_1", "file_name": "python.txt", "page_number": 1}
        chunk2 = Chunk(
            chunk_id="chk_2",
            document_id="doc_1",
            file_name="python.txt",
            text="FastAPI is a modern web framework for Python.",
            page_number=1,
            chunk_index=1,
            metadata=meta2
        )
        
        embeddings = model.encode([chunk1.text, chunk2.text])
        store.add_chunks([chunk1, chunk2], embeddings)
        
        query_emb = model.encode(["web framework"])[0]
        results = store.search(query_emb, top_k=2)
        
        assert len(results) > 0
        assert "FastAPI" in results[0]["text"]
        assert results[0]["similarity"] > 0.0
    finally:
        settings.CHROMA_PATH = original_path
