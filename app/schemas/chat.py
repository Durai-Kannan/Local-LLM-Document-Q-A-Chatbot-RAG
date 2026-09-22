from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The query/question asked by the user.")
    top_k: Optional[int] = Field(default=None, description="Number of top context chunks to retrieve.")

class SourceReference(BaseModel):
    document: str
    page: Optional[int] = None
    chunk_id: str
    relevance_score: Optional[float] = None
    snippet: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
    context_used: bool = True

class HealthResponse(BaseModel):
    status: str
    ollama: bool
    ollama_model: str
    vector_db: bool
    total_documents: int
    total_chunks: int
