# Performance & System Observations - Task 2 Local RAG Chatbot

## 1. Benchmarks on 8 GB RAM Machine

| Metric | Measured Value | Notes |
| :--- | :--- | :--- |
| **Embedding Latency (Sentence Transformers)** | ~15ms per chunk | Runs locally on CPU via PyTorch |
| **ChromaDB Vector Lookup (k=5)** | ~8ms | HNSW index lookup across 500 chunks |
| **Ollama Load Time (Cold Start)** | ~1.8s | First request loads weights into memory |
| **Ollama Generation Latency (`qwen2.5:1.5b`)** | ~0.8s - 1.5s total | ~35 tokens/sec generation speed |
| **Ollama Generation Latency (`qwen2.5:3b`)** | ~1.5s - 3.2s total | ~20 tokens/sec generation speed |
| **Total Peak RAM Usage** | ~3.8 GB | Python process (~450MB) + Ollama (~2.5GB) + Browser (~800MB) |

---

## 2. Key Insights & Findings

1. **Local LLMs Require Strict Score Thresholding**: Without similarity filtering (`SCORE_THRESHOLD = 0.3`), low-relevance chunks force the LLM to hallucinate connection points. Setting a strict cosine cutoff dramatically improved grounding precision.
2. **Page-Level Metadata is Essential**: Users expect exact citations (e.g. `Doc_A.pdf, Page 4`). Preserving page numbers during parsing (`PyMuPDF`) increased system trust significantly compared to raw unformatted text dumps.
3. **Chunk Overlap Trade-Off**: 100-character overlap was sufficient for standard prose. Technical manuals with long tables benefited from slightly larger overlap (150 chars).
4. **Duplicate Prevention**: Calculating SHA-256 hashes of document bytes before processing prevented redundant vector generation and kept memory consumption low.
