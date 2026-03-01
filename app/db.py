"""
db.py — PostgreSQL connection and schema initialisation.

Reads all credentials from environment variables so that no secrets
are ever hardcoded in source code.

Required env vars:
    DB_HOST      (default: localhost)
    DB_PORT      (default: 5432)
    DB_NAME      (default: ragdb)
    DB_USER      (default: postgres)
    DB_PASSWORD  (required – no default)
"""

import os
import psycopg2


def get_connection() -> psycopg2.extensions.connection:
    """
    Open and return a new PostgreSQL connection.
    Raises a clear error if the database cannot be reached.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "ragdb"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        return conn
    except psycopg2.OperationalError as e:
        print("\n[ERROR] Could not connect to PostgreSQL.")
        print(f"        Details: {e}")
        print("        Make sure PostgreSQL is running and the following")
        print("        environment variables are set correctly:")
        print("          DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        raise


def init_db() -> None:
    """
    Enable the pgvector extension and create the ncert_chunks table
    if it does not already exist.

    Table schema:
        id        SERIAL PRIMARY KEY
        subject   TEXT              — 'science' or 'english'
        context   TEXT              — raw textbook passage
        embedding VECTOR(768)       — nomic-embed-text produces 768-dim vectors
    """
    conn = get_connection()
    cur = conn.cursor()

    # pgvector extension must exist before VECTOR type can be used
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ncert_chunks (
            id        SERIAL PRIMARY KEY,
            subject   TEXT,
            context   TEXT,
            embedding VECTOR(768)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("[DB] Extension and table ready.")
