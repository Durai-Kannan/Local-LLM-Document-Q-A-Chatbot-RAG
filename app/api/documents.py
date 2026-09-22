from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.vectorstore.chroma_store import ChromaVectorStore
from app.services.document_service import DocumentService
from app.core.logging_config import logger

router = APIRouter(prefix="/api/documents", tags=["Documents"])

def get_document_service() -> DocumentService:
    vector_store = ChromaVectorStore()
    return DocumentService(vector_store=vector_store)

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided or invalid filename.")

    allowed_exts = [".pdf", ".docx", ".txt", ".md"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_ext}'. Allowed formats: PDF, DOCX, TXT, MD."
        )

    try:
        contents = await file.read()
        doc_service = get_document_service()
        result = doc_service.upload_document(file.filename, contents)
        
        return DocumentResponse(
            document_id=result["document_id"],
            file_name=result["file_name"],
            file_type=result.get("file_type", file_ext),
            file_size=result.get("file_size", len(contents)),
            created_at=result.get("created_at", ""),
            total_chunks=result.get("total_chunks", 0)
        )
    except ValueError as e:
        logger.warning(f"Validation error during upload: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

@router.get("", response_model=DocumentListResponse)
async def list_documents():
    doc_service = get_document_service()
    documents = doc_service.list_documents()
    res_docs = [
        DocumentResponse(
            document_id=d["document_id"],
            file_name=d.get("file_name", "Unknown"),
            file_type=d.get("file_type", "unknown"),
            file_size=d.get("file_size", 0),
            created_at=d.get("created_at", ""),
            total_chunks=d.get("total_chunks", 0)
        )
        for d in documents
    ]
    return DocumentListResponse(documents=res_docs, total=len(res_docs))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    doc_service = get_document_service()
    success = doc_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found.")
    return {"status": "success", "message": f"Document '{document_id}' deleted successfully."}
