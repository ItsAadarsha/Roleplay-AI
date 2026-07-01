# backend/app/routers/documents.py
import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.documents import chunk_document, embed_chunks
from app.services.vectorstore import save_chunks_to_chromadb

router = APIRouter(prefix="/story", tags=["documents"])

UPLOAD_DIR = "app/data/uploads"
ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/{id}/docs")
async def create_story_document(id: str, file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            chunks = chunk_document(temp_path)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Failed to process document: {e}")

        if not chunks:
            raise HTTPException(status_code=422, detail="No content could be extracted from the document")

        embeddings = embed_chunks(chunks)

        result = save_chunks_to_chromadb(
            chunks=chunks,
            embeddings=embeddings,
            session_id=id,
            source_pdf=file.filename,
            collection_type="lore",
        )

        return {
            "status": "success",
            "session_id": id,
            "source_pdf": file.filename,
            **result,
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)