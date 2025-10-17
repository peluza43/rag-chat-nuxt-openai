import os
chroma = chromadb.PersistentClient(path=PERSIST_DIR, settings=Settings(anonymized_telemetry=False))


def get_or_create_collection(name: str):
try:
return chroma.get_collection(name)
except Exception:
return chroma.create_collection(name)




def pdf_to_chunks(pdf_path: str, chunk_size=1000, chunk_overlap=150) -> List[str]:
reader = PdfReader(pdf_path)
full_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
return splitter.split_text(full_text)




def embed_texts(texts: List[str]) -> List[List[float]]:
# OpenAI embeddings (batched)
resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
return [d.embedding for d in resp.data]




def ingest_pdf(pdf_path: str, collection_name: str = DEFAULT_COLLECTION) -> Tuple[str, int]:
col = get_or_create_collection(collection_name)
chunks = pdf_to_chunks(pdf_path)
if not chunks:
return ("", 0)
vectors = embed_texts(chunks)
ids = [f"{os.path.basename(pdf_path)}::{i}" for i in range(len(chunks))]
metadatas = [{"source": os.path.basename(pdf_path), "index": i} for i in range(len(chunks))]
col.add(documents=chunks, metadatas=metadatas, embeddings=vectors, ids=ids)
return (os.path.basename(pdf_path), len(chunks))




def retrieve(query: str, collection_name: str, top_k=4):
col = get_or_create_collection(collection_name)
q_emb = embed_texts([query])[0]
res = col.query(query_embeddings=[q_emb], n_results=top_k, include=["documents", "metadatas", "distances"])
docs = res.get("documents", [[]])[0]
metas = res.get("metadatas", [[]])[0]
dists = res.get("distances", [[]])[0]
# Chroma devuelve distancia; convertimos a pseudo-similaridad
sims = [1.0 - float(d) if d is not None else 0.0 for d in dists]
return list(zip(docs, metas, sims))




def build_prompt(question: str, contexts: List[str]) -> str:
joined = "\n\n---\n\n".join(contexts)
system = (
"Eres un asistente que responde SOLO usando el contenido del documento proporcionado.\n"
"Si la respuesta no está en el documento, debes responder exactamente: \n"
"\"No poseo información sobre ese tema en el documento cargado.\"\n"
"Cita brevemente la sección (página/índice si se conoce)."
)
user = f"Documento (fragmentos):\n\n{joined}\n\nPregunta: {question}\n\nResponde en español."
return system, user




def answer_with_rag(question: str, collection_name: str, top_k=4, min_score=0.35):
retrieved = retrieve(question, collection_name, top_k=top_k)
filtered = [(t, m, s) for (t, m, s) in retrieved if s >= min_score]


if not filtered:
return {
"answer": "No poseo información sobre ese tema en el documento cargado.",
"sources": [],
"used_context": False,
}


contexts = [t for (t, _, _) in filtered]
system, user = build_prompt(question, contexts)


stream = client.chat.completions.create(
model=CHAT_MODEL,
messages=[
{"role": "system", "content": system},
{"role": "user", "content": user},
],
stream=True,
temperature=0.2,
)
return {"stream": stream, "sources": filtered, "used_context": True}