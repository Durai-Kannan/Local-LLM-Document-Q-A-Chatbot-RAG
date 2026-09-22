from typing import Dict, Any, Optional
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import DocumentRetriever
from app.llm.ollama_client import OllamaClient
from app.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, build_context_string
from app.schemas.chat import ChatResponse, SourceReference
from app.core.logging_config import logger

class RAGService:
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.retriever = DocumentRetriever(vector_store=vector_store)
        self.ollama_client = OllamaClient()

    async def answer_question(self, question: str, top_k: Optional[int] = None) -> ChatResponse:
        logger.info(f"Processing Q&A request for question: '{question}'")

        retrieved_chunks, sources = self.retriever.retrieve(query=question, top_k=top_k)

        if not retrieved_chunks:
            logger.info("No relevant context found matching the query threshold.")
            return ChatResponse(
                answer="No relevant information was found in the uploaded documents to answer your question.",
                sources=[],
                context_used=False
            )

        context_text = build_context_string(retrieved_chunks)
        user_prompt = USER_PROMPT_TEMPLATE.format(context=context_text, question=question)

        try:
            raw_answer = await self.ollama_client.generate(
                prompt=user_prompt,
                system_prompt=SYSTEM_PROMPT
            )
            return ChatResponse(
                answer=raw_answer,
                sources=sources,
                context_used=True
            )
        except Exception as e:
            logger.error(f"Error during RAG generation: {str(e)}")
            raise e
