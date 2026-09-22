from fastapi import APIRouter, Depends
from app.schemas.chat import HealthResponse
from app.llm.ollama_client import OllamaClient
from app.vectorstore.chroma_store import ChromaVectorStore
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    ollama_client = OllamaClient()
    ollama_health = await ollama_client.check_health()
    
    chroma_store = ChromaVectorStore()
    total_chunks = chroma_store.count_chunks()
    documents = chroma_store.get_all_documents()
    
    overall_status = "ok" if (ollama_health.get("available") and ollama_health.get("model_found")) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        ollama=ollama_health.get("available", False),
        ollama_model=settings.OLLAMA_MODEL,
        vector_db=True,
        total_documents=len(documents),
        total_chunks=total_chunks
    )
