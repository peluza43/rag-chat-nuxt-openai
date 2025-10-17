import os
from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv
from .rag import ingest_pdf
from .utils import UPLOAD_DIR
from .models import UploadResponse


router = APIRouter(prefix="/api")


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), collection: str | None = None):
collection = collection or os.getenv("CHROMA_COLLECTION", "docs")
# Guardar archivo
dest = UPLOAD_DIR / file.filename
with open(dest, "wb") as f:
f.write(await file.read())
doc_id, chunks = ingest_pdf(str(dest), collection_name=collection)
return UploadResponse(collection=collection, doc_id=doc_id, chunks=chunks)