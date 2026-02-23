# NCERT Local RAG System

A fully **local**, **CPU-compatible** Retrieval-Augmented Generation (RAG) system
built over NCERT Class 6–8 Science and English textbooks.

| Component | Tool |
|---|---|
| Embeddings | `nomic-embed-text` via Ollama |
| LLM | `gemma3:1b` via Ollama |
| Vector store | PostgreSQL + pgvector |
| Backend | Python 3.10+ |

No OpenAI. No cloud calls. Everything runs on your machine.

---

## Project Structure

```
ollama-rag/
├── app/
│    ├── __init__.py
│    ├── db.py          # PostgreSQL connection & schema
│    ├── embed.py       # Ollama embedding function
│    ├── indexer.py     # CSV → embeddings → DB
│    ├── retriever.py   # Vector similarity search
│    ├── generator.py   # Ollama LLM generation
│    └── main.py        # CLI entry point
├── dataset/
│    ├── science/
│    └── english/
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- [Ollama](https://ollama.com/) installed

---

## Step 1 — Install pgvector

pgvector adds vector similarity search to PostgreSQL.

```bash
# Install build dependencies
sudo apt-get install postgresql-server-dev-all build-essential git -y

# Build and install pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
cd ..
```

Then enable it inside your database:

```bash
psql -U postgres -d ragdb -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

> If the database does not exist yet, create it first:
> ```bash
> psql -U postgres -c "CREATE DATABASE ragdb;"
> ```

---

## Step 2 — Pull Ollama Models

```bash
# Embedding model (768-dim vectors, optimised for retrieval)
ollama pull nomic-embed-text

# Generation model (small, fast, CPU-friendly)
ollama pull gemma3:1b
```

Make sure Ollama is running before using the system:

```bash
ollama serve
```

---

## Step 3 — Set Environment Variables

Never hardcode your database password. Export these before running:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ragdb
export DB_USER=postgres
export DB_PASSWORD=your_password_here
```

For convenience, add these to a `.env` file (do **not** commit it):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ragdb
DB_USER=postgres
DB_PASSWORD=your_password_here
```

Then load with: `export $(cat .env | xargs)`

---

## Step 4 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5 — Index the Dataset

This reads all CSV files, generates embeddings, and stores them in PostgreSQL.
It is **safe to re-run** — duplicate contexts are automatically skipped.

```bash
python -m app.indexer
```

Expected output:

```
[Indexer] Initialising database ...
[DB] Extension and table ready.

[Indexer] Processing: .../dataset/science/ncert-class6-8-science-combined.csv
[Indexer] 97 unique contexts found.
  → 10/97 processed  (10 inserted, 0 skipped)
  ...
[Indexer] Finished 'science': 97 inserted, 0 already existed.

[Indexer] Processing: .../dataset/english/ncert-class6-8-english-combined.csv
...
[Indexer] All files processed. Ready to query.
```

Indexing time depends on your CPU speed. Expect a few minutes.

---

## Step 6 — Run the CLI

```bash
python -m app.main
```

Example session:

```
╔══════════════════════════════════════════════════════════╗
║          NCERT RAG System  —  Local & Fully Private      ║
║    Powered by Ollama · nomic-embed-text · gemma3:1b      ║
║              Type  exit  or  quit  to stop               ║
╚══════════════════════════════════════════════════════════╝

Your Question: What are herbivores?

[*] Searching for relevant context ...
[*] Retrieved 3 passage(s) from: science
[*] Generating answer ...

────────────────────────────────────────────────────────────
Herbivores are animals that eat only plants or plant products.
────────────────────────────────────────────────────────────

Your Question: exit
Goodbye!
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Cannot reach Ollama` | Run `ollama serve` in a separate terminal |
| `Could not connect to PostgreSQL` | Check `DB_*` env vars and ensure PostgreSQL is running |
| `model not found` | Run `ollama pull nomic-embed-text` and `ollama pull gemma3:1b` |
| No results returned | Run `python -m app.indexer` first |

---

## Dataset

NCERT Class 6–8 Science and English textbook passages (~739 unique Q&A contexts).

- Source: [theshivam7/ncert-dataset](https://huggingface.co/datasets/theshivam7/ncert-dataset)
- License: CC BY 4.0
- Paper: [Pustak AI (arXiv:2511.10002)](https://arxiv.org/html/2511.10002v2)
