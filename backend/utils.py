import os
from pathlib import Path


UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./storage/uploads")).resolve()
PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", "./storage/chroma")).resolve()


for d in (UPLOAD_DIR, PERSIST_DIR):
d.mkdir(parents=True, exist_ok=True)