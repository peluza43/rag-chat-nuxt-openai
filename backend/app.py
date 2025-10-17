import os
from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .ingest import router as ingest_router
from .rag import answer_with_rag


ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")


# Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=ALLOWED_ORIGINS)
app = FastAPI()


app.add_middleware(
CORSMiddleware,
allow_origins=ALLOWED_ORIGINS,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


app.include_router(ingest_router)


@sio.event
async def connect(sid, environ):
print("Cliente conectado:", sid)


@sio.event
async def disconnect(sid):
print("Cliente desconectado:", sid)


@sio.event
async def ask(sid, data):
"""
data = { question: str, collection: str, top_k?: int, min_score?: float }
Emite eventos:
- answer_chunk { text }
- answer_done { sources, used_context }
"""
question = data.get("question", "").strip()
collection = data.get("collection") or os.getenv("CHROMA_COLLECTION", "docs")
top_k = int(data.get("top_k", 4))
min_score = float(data.get("min_score", 0.35))


if not question:
await sio.emit("answer_done", {"sources": [], "used_context": False, "error": "Pregunta vacía."}, to=sid)
return


result = answer_with_rag(question, collection, top_k=top_k, min_score=min_score)


if "stream" not in result:
# Respuesta directa (sin contexto)
await sio.emit("answer_chunk", {"text": result["answer"]}, to=sid)
await sio.emit("answer_done", {"sources": [], "used_context": False}, to=sid)
return


stream = result["stream"]
sources = result["sources"]


try:
async for event in stream:
delta = event.choices[0].delta.content or ""
if delta:
await sio.emit("answer_chunk", {"text": delta}, to=sid)
except Exception as e:
await sio.emit("answer_chunk", {"text": f"\n[Streaming interrumpido: {e}]"}, to=sid)
finally:
# Enviar fuentes compactas
compact_sources = [
{
"text": t[:180] + ("…" if len(t) > 180 else ""),
"score": float(s),
"metadata": m,
} for (t, m, s) in sources
]
await sio.emit("answer_done", {"sources": compact_sources, "used_context": True}, to=sid)


# Montar la app ASGI de Socket.IO junto a FastAPI
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)


# Ejecutar: uvicorn backend.app:asgi_app --reload --port 8000