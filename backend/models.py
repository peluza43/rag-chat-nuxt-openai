from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
collection: str
doc_id: str
chunks: int


class AskPayload(BaseModel):
question: str
collection: str
top_k: int = 4
min_score: float = 0.35 # umbral de similitud


class RetrievedChunk(BaseModel):
text: str
score: float
metadata: dict


class AskResult(BaseModel):
answer: str
sources: List[RetrievedChunk]
used_context: bool