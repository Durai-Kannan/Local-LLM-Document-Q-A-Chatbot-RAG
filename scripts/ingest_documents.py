import os
import sys
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.vectorstore.chroma_store import ChromaVectorStore
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.core.logging_config import logger

def main():
    parser = argparse.ArgumentParser(description="Task 2 Local RAG - Document Ingestion CLI Tool")
    parser.add_argument(
        "--path",
        type=str,
        default="./data/documents",
        help="Path to directory or single document file to ingest (default: ./data/documents)"
    )
    args = parser.parse_args()

    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"Error: Target path '{target_path}' does not exist.")
        sys.exit(1)

    vector_store = ChromaVectorStore()
    pipeline = DocumentIngestionPipeline(vector_store=vector_store)

    files_to_ingest = []
    if os.path.isfile(target_path):
        files_to_ingest.append(target_path)
    else:
        for root, _, files in os.walk(target_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [".pdf", ".docx", ".txt", ".md"]:
                    files_to_ingest.append(os.path.join(root, file))

    if not files_to_ingest:
        print(f"No supported documents (.pdf, .docx, .txt, .md) found in '{target_path}'.")
        return

    print(f"Found {len(files_to_ingest)} document(s) to ingest...")
    success_count = 0
    skipped_count = 0

    for file_path in files_to_ingest:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing: {file_name}")
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            result = pipeline.process_file(file_name=file_name, file_bytes=file_bytes)
            if result.get("status") == "already_exists":
                print(f" -> SKIPPED (Already ingested): {file_name}")
                skipped_count += 1
            else:
                print(f" -> SUCCESS: Ingested {result.get('total_chunks')} chunks across {result.get('total_pages')} page(s).")
                success_count += 1
        except Exception as e:
            print(f" -> FAILED: {file_name} - Error: {e}")

    print("\n" + "=" * 50)
    print(f"Ingestion Summary: {success_count} succeeded, {skipped_count} skipped, Total chunks in ChromaDB: {vector_store.count_chunks()}")
    print("=" * 50)

if __name__ == "__main__":
    main()
