"""
retriever.py — Semantic similarity search over the pgvector store.

Given a user question:
  1. Embed the question using nomic-embed-text.
  2. Query PostgreSQL with the <-> (L2 distance) operator to find the
     closest stored context vectors.
  3. Return the top-k results as a list of dicts.
"""

from app.db import get_connection
from app.embed import get_embedding


def retrieve_contexts(question: str, top_k: int = 3) -> list:
    """
    Find the most semantically similar NCERT passages for a given question.

    Args:
        question: The user's natural-language question.
        top_k:    Number of context passages to return (default: 3).

    Returns:
        A list of dicts with keys 'subject' and 'context', ordered by
        ascending L2 distance (most relevant first).
    """
    # Embed the question into the same 768-dim space as the stored passages
    question_embedding = get_embedding(question)

    conn = get_connection()
    cur = conn.cursor()

    # <-> is pgvector's L2 distance operator; smaller = more similar
    cur.execute(
        """
        SELECT subject, context
        FROM   ncert_chunks
        ORDER  BY embedding <-> %s::vector DESC
        LIMIT  %s;
        """,
        (question_embedding, top_k),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"subject": row[0], "context": row[1]} for row in rows]
