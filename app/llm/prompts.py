SYSTEM_PROMPT = """You are a precise, grounded document question-answering assistant.

RULES:
1. Answer the user's question using ONLY the provided document context below.
2. Do NOT use any outside knowledge or assumptions not present in the context.
3. If the answer cannot be found or deduced from the provided context, state clearly: "The requested information is not available in the uploaded documents."
4. Do NOT invent, assume, or extrapolate facts.
5. Whenever you provide information, reference the relevant source tag e.g. [Source 1], [Source 2] matching the provided context sections.
"""

USER_PROMPT_TEMPLATE = """Context:
{context}

Question:
{question}

Answer:"""

def build_context_string(retrieved_chunks: list) -> str:
    if not retrieved_chunks:
        return "No relevant document context found."

    context_parts = []
    for idx, item in enumerate(retrieved_chunks, start=1):
        metadata = item.get("metadata", {})
        file_name = metadata.get("file_name", "Unknown Document")
        page = metadata.get("page_number")
        chunk_id = item.get("chunk_id", "")
        
        page_str = f" | Page {page}" if page else ""
        header = f"[Source {idx}] Document: {file_name}{page_str} (Chunk: {chunk_id})"
        body = item.get("text", "").strip()
        context_parts.append(f"{header}\n{body}")

    return "\n\n---\n\n".join(context_parts)
