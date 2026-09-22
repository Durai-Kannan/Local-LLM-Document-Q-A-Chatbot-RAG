# Implementation Notes - Task 2 Local RAG Chatbot

## 1. Engineering Decisions & Rationale

### A. ChromaDB vs FAISS vs SQLite Vector
- **Selection**: ChromaDB Persistent Client.
- **Rationale**: ChromaDB provides native metadata storage, persistent disk-backed HNSW indexing, and single-package Python installation without complex external dependencies. This makes Task 2 completely modular compared to SQLite/FAISS in Task 1.

### B. Ollama Model Choice: `qwen2.5:1.5b` vs `qwen2.5:3b`
- **Hardware Target**: 8 GB RAM Laptop with integrated graphics or standard quad-core CPU.
- **Decision**: Default to `qwen2.5:1.5b` or `qwen2.5:3b`.
- **Reasoning**:
  - `qwen2.5:1.5b` requires ~1.2 GB of VRAM/RAM, delivering ~25-40 tokens/sec.
  - `qwen2.5:3b` requires ~2.5 GB of RAM, offering superior instruction-following and prompt grounding while easily fitting into standard memory constraints.

### C. Chunk Size & Overlap Sizing
- **Chunk Size (700 characters)**: Optimized to fit 3-5 distinct semantic paragraphs while maintaining high granularity during top-k vector search.
- **Chunk Overlap (100 characters)**: Prevents sentence truncation across chunk boundaries, ensuring entities spanning multiple sentences retain full contextual embeddings.

---

## 2. Grounding & Anti-Hallucination Design

To guarantee zero hallucination when documents do not contain the user's answer:
1. **Cosine Distance Filtering**: ChromaDB returns distance values (`dist`). We compute `similarity = 1.0 - dist`. Chunks with `similarity < 0.3` are discarded.
2. **Strict System Prompting**:
   ```text
   You are an assistant for question-answering tasks.
   Use ONLY the following retrieved pieces of context to answer the question.
   If you do not know the answer based on the context, state:
   "No relevant information was found in the uploaded documents."
   Do NOT use outside knowledge.
   ```
3. **Fallback Detection**: If zero chunks pass the similarity threshold, the RAG service returns a direct static fallback response without calling Ollama, saving inference time.

---

## 3. UI/UX Design

- **Glassmorphism Theme**: Dark mode palette with subtle backdrop blur (`backdrop-filter: blur(12px)`), radiant purple gradients (`#8a2be2`), and responsive flex layout.
- **Citation Inspector**: Each assistant response renders interactive pill badges. Clicking a citation opens a modal overlay displaying the exact file, page number, similarity score, and full chunk text snippet.
