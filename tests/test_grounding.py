import asyncio
import pytest
from app.services.rag_service import RAGService
from app.vectorstore.chroma_store import ChromaVectorStore

def test_rag_fallback_when_no_context():
    vector_store = ChromaVectorStore()
    rag_service = RAGService(vector_store=vector_store)
    
    # Ask a question that won't match any document
    response = asyncio.run(rag_service.answer_question(
        question="What is the quantum telemetry frequency of Martian satellite ZX-999?",
        top_k=5
    ))
    assert response is not None
    assert "No relevant information was found" in response.answer or len(response.sources) == 0
