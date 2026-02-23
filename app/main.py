"""
main.py — CLI entry point for the NCERT RAG system.

Run with:
    python -m app.main

The loop:
  1. Prompt the user for a question.
  2. Retrieve the top-3 most relevant NCERT passages from PostgreSQL.
  3. Feed the question + passages to gemma3:1b via Ollama.
  4. Print the grounded answer.
"""

import sys

from app.retriever import retrieve_contexts
from app.generator import generate_answer


BANNER = """
╔══════════════════════════════════════════════════════════╗
║          NCERT RAG System  —  Local & Fully Private      ║
║    Powered by Ollama · nomic-embed-text · gemma3:1b      ║
║              Type  exit  or  quit  to stop               ║
╚══════════════════════════════════════════════════════════╝
"""


def run() -> None:
    """Main interactive loop."""
    print(BANNER)

    while True:
        try:
            question = input("Your Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl-D / Ctrl-C gracefully
            print("\nGoodbye!")
            sys.exit(0)

        if not question:
            continue

        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            sys.exit(0)

        try:
            print("\n[*] Searching for relevant context ...")
            contexts = retrieve_contexts(question, top_k=3)

            if not contexts:
                print("[!] No context found. Run the indexer first:")
                print("        python -m app.indexer")
                continue

            subjects = ", ".join(sorted({c["subject"] for c in contexts}))
            print(f"[*] Retrieved {len(contexts)} passage(s) from: {subjects}")
            print("[*] Generating answer ...\n")

            answer = generate_answer(question, contexts)

            print("─" * 60)
            print(answer)
            print("─" * 60)

        except Exception:
            # Specific error messages are already printed inside each module
            print("[!] Skipping this question due to the error above.\n")


if __name__ == "__main__":
    run()
