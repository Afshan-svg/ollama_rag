"""
api.py — HTTP API for the NCERT RAG system.

Run with:
    uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET  /health   — health check
    POST /query    — retrieve chunks from vector DB + optional LLM answer
    POST /retrieve — retrieve only top-k chunks from vector DB (no LLM)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.retriever import retrieve_contexts
from app.generator import generate_answer

app = FastAPI(title="NCERT RAG API", version="1.0")


# ── Request/Response models ─────────────────────────────────────────────────


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    generate_answer: bool = True  # if False, only return chunks from vector DB


class ChunkResponse(BaseModel):
    subject: str
    context: str


class QueryResponse(BaseModel):
    question: str
    chunks: list[ChunkResponse]
    answer: str | None = None  # None when generate_answer=False


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    """Health check for load balancers / readiness probes."""
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Get relevant chunks from the vector DB and optionally generate an answer.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question must be non-empty")

    chunks = retrieve_contexts(request.question, top_k=request.top_k)
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No context found. Run the indexer first.",
        )

    out_chunks = [
        ChunkResponse(subject=c["subject"], context=c["context"]) for c in chunks
    ]
    answer = None
    if request.generate_answer:
        answer = generate_answer(request.question, chunks)

    return QueryResponse(question=request.question, chunks=out_chunks, answer=answer)


@app.post("/retrieve", response_model=list[ChunkResponse])
def retrieve_only(request: QueryRequest):
    """Return only the top-k chunks from the vector DB (no LLM)."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question must be non-empty")

    chunks = retrieve_contexts(request.question, top_k=request.top_k)
    if not chunks:
        raise HTTPException(status_code=404, detail="No context found.")

    return [ChunkResponse(subject=c["subject"], context=c["context"]) for c in chunks]
