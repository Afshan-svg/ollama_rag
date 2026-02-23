"""
indexer.py — Load CSV files, chunk long passages, and populate the PostgreSQL vector store.

The NCERT context column contains entire textbook chapters (often 3000–6000 words).
Embedding a full chapter as one vector:
  (a) exceeds nomic-embed-text's token limit → Ollama 500 error
  (b) produces poor retrieval because the vector blends too many topics

Solution: split each context into overlapping word-level chunks before embedding.
Each chunk becomes one row in ncert_chunks with its own 768-dim vector.

Pipeline per CSV file:
  1. Load and deduplicate raw contexts.
  2. Split each context into chunks of CHUNK_SIZE words with CHUNK_OVERLAP overlap.
  3. Skip chunks already stored (idempotent — safe to re-run).
  4. Embed each chunk via nomic-embed-text.
  5. Insert (subject, chunk_text, embedding) into ncert_chunks.
"""

import os
import pandas as pd

from app.db import get_connection, init_db
from app.embed import get_embedding


# ── Chunking parameters ──────────────────────────────────────────────────────
# nomic-embed-text handles up to ~8192 tokens. 300 words ≈ 400–450 tokens,
# well within the limit and short enough to embed a focused concept.
CHUNK_SIZE    = 300   # words per chunk
CHUNK_OVERLAP = 50    # words shared between consecutive chunks to preserve context

# ── Dataset files ─────────────────────────────────────────────────────────────
# All CSV files to index, relative to the project root.
# Duplicates (combined vs individual) are skipped automatically.
DATASET_FILES = [
    # Science — individual classes
    ("dataset/science/ncert-class6-science.csv",            "science"),
    ("dataset/science/ncert-class7-science.csv",            "science"),
    ("dataset/science/ncert-class8-science.csv",            "science"),
    # Science — combined (Class 6–8)
    ("dataset/science/ncert-class6-8-science-combined.csv", "science"),
    # English — individual classes
    ("dataset/english/ncert-class6-english.csv",            "english"),
    ("dataset/english/ncert-class7-english.csv",            "english"),
    ("dataset/english/ncert-class8-english.csv",            "english"),
    # English — combined (Class 6–8)
    ("dataset/english/ncert-class6-8-english-combined.csv", "english"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_csv(filepath: str) -> pd.DataFrame:
    """Read a CSV file and validate that it contains a 'context' column."""
    df = pd.read_csv(filepath)
    if "context" not in df.columns:
        raise ValueError(
            f"Expected a 'context' column in {filepath}. "
            f"Found columns: {df.columns.tolist()}"
        )
    return df


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """
    Split text into overlapping word-level chunks.

    Args:
        text:       The raw passage to split.
        chunk_size: Maximum number of words per chunk.
        overlap:    Number of words repeated at the start of the next chunk
                    to preserve context across chunk boundaries.

    Returns:
        A list of non-empty chunk strings.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # Advance by (chunk_size - overlap) so the next chunk re-uses the tail
        start += chunk_size + overlap

    return chunks


def chunk_exists(cur, chunk: str) -> bool:
    """Return True if this exact chunk text is already stored in the DB."""
    cur.execute(
        "SELECT 1 FROM ncert_chunks WHERE context = %s LIMIT 1;",
        (chunk,),
    )
    return cur.fetchone() is not None


# ── Core indexing logic ───────────────────────────────────────────────────────

def index_file(filepath: str, subject: str) -> None:
    """
    Chunk, embed, and store every passage from a single CSV file.

    Args:
        filepath: Absolute path to the CSV file.
        subject:  Label stored with each row ('science' or 'english').
    """
    print(f"\n[Indexer] Processing: {filepath}")
    df = load_csv(filepath)

    # Deduplicate raw contexts within the file before chunking
    unique_contexts = df["context"].dropna().unique().tolist()
    print(f"[Indexer] {len(unique_contexts)} unique contexts → chunking ...")

    # Pre-generate all chunks so we can show a meaningful total count
    all_chunks = []
    for context in unique_contexts:
        context = str(context).strip()
        if context:
            all_chunks.extend(chunk_text(context))

    total = len(all_chunks)
    print(f"[Indexer] {total} chunks to process (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    conn = get_connection()
    cur = conn.cursor()
    inserted = skipped = 0

    for i, chunk in enumerate(all_chunks, start=1):
        # Idempotent: skip chunks that were already embedded and stored
        if chunk_exists(cur, chunk):
            skipped += 1
            continue

        embedding = get_embedding(chunk)

        cur.execute(
            "INSERT INTO ncert_chunks (subject, context, embedding) VALUES (%s, %s, %s);",
            (subject, chunk, embedding),
        )
        inserted += 1

        # Commit every 10 inserts to keep transactions small
        if inserted % 10 == 0:
            conn.commit()
            print(f"  → {i}/{total}  ({inserted} inserted, {skipped} skipped)")

    conn.commit()
    cur.close()
    conn.close()
    print(f"[Indexer] Done '{subject}': {inserted} inserted, {skipped} already existed.")


def run_indexer() -> None:
    """Initialise the DB schema, then index all configured CSV files."""
    print("[Indexer] Initialising database ...")
    init_db()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for relative_path, subject in DATASET_FILES:
        filepath = os.path.join(project_root, relative_path)
        if os.path.exists(filepath):
            index_file(filepath, subject)
        else:
            print(f"[WARNING] File not found, skipping: {filepath}")

    print("\n[Indexer] All files processed. Ready to query.")


if __name__ == "__main__":
    run_indexer()
