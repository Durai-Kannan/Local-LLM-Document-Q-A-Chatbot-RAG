# Task 2 Demo Video Guide

This directory contains the video demonstration recording for **Task 2 - Local LLM RAG Chatbot**.

## Suggested 2-3 Minute Recording Timeline

- **0:00 - 0:15**: Display Ollama daemon running locally in terminal (`ollama list` showing `qwen2.5`).
- **0:15 - 0:30**: Start FastAPI backend (`python run.py`) and open `http://localhost:8000`.
- **0:30 - 1:00**: Upload a sample PDF/DOCX document via UI drag-and-drop; highlight chunking and embedding feedback.
- **1:00 - 1:40**: Type a domain-specific question; demonstrate instant RAG context retrieval and LLM response.
- **1:40 - 2:00**: Click the source citation pill to view the modal with exact page number and text snippet.
- **2:00 - 2:30**: Demonstrate anti-hallucination by asking an out-of-context question and receiving the fallback warning.
