from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.vectorstore.chroma_store import ChromaVectorStore
from app.services.rag_service import RAGService
from app.core.logging_config import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

def get_rag_service() -> RAGService:
    vector_store = ChromaVectorStore()
    return RAGService(vector_store=vector_store)

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        rag_service = get_rag_service()
        response = await rag_service.answer_question(
            question=request.question.strip(),
            top_k=request.top_k
        )
        return response
    except RuntimeError as e:
        err_msg = str(e)
        if "Could not connect to Ollama" in err_msg or "timed out" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=err_msg
            )
        raise HTTPException(status_code=500, detail=err_msg)
    except Exception as e:
        logger.error(f"Unexpected error in /api/chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal chat error: {str(e)}")
