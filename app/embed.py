"""
embed.py — Text embedding via the Ollama API.

Uses the nomic-embed-text model which produces 768-dimensional vectors
optimised for retrieval / semantic similarity tasks.
"""

import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list:
    """
    Send text to the Ollama embeddings endpoint and return the
    768-dimensional float vector.

    Args:
        text: The string to embed (a passage or a question).

    Returns:
        A list of 768 floats representing the semantic vector.

    Raises:
        requests.exceptions.ConnectionError  — if Ollama is not running.
        requests.exceptions.HTTPError        — if the model is not pulled.
    """
    try:
        response = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot reach Ollama at http://localhost:11434")
        print("        Start Ollama with:  ollama serve")
        raise

    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Ollama embeddings API returned an error: {e}")
        try:
            print(f"        Response body: {e.response.text[:300]}")
        except Exception:
            pass
        print(f"        Make sure the model is pulled:  ollama pull {EMBED_MODEL}")
        raise
