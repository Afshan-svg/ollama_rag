"""
generator.py — Answer generation via the Ollama LLM API.

Uses gemma3:1b to produce a grounded answer from retrieved contexts.
The prompt is structured so the model is instructed to rely only on the
provided passages, reducing hallucination on out-of-scope questions.
"""

import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "gemma3:1b"


def build_prompt(question: str, contexts: list) -> str:
    """
    Construct the RAG prompt by injecting retrieved context passages
    before the question.

    Args:
        question: The user's question.
        contexts: List of dicts with 'subject' and 'context' keys.

    Returns:
        A fully formatted prompt string ready for the LLM.
    """
    context_block = "\n\n---\n\n".join(
        f"[{c['subject'].upper()} TEXTBOOK]\n{c['context']}"
        for c in contexts
    )

    return f"""You are a helpful educational assistant for NCERT school textbooks (Classes 6–8).
Use ONLY the context passages provided below to answer the question.
Be concise and accurate. If the answer cannot be found in the context, respond with:
"I don't have enough information in the provided context to answer this."

CONTEXT:
{context_block}

QUESTION: {question}

ANSWER:"""


def generate_answer(question: str, contexts: list) -> str:
    """
    Send the RAG prompt to Ollama and return the generated answer.

    Args:
        question: The user's question.
        contexts: Retrieved context passages from the vector store.

    Returns:
        The model's answer as a plain string.

    Raises:
        requests.exceptions.ConnectionError — if Ollama is not running.
        requests.exceptions.HTTPError       — if the model is not pulled.
    """
    prompt = build_prompt(question, contexts)

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": True,    # receive the complete response at once
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot reach Ollama at http://localhost:11434")
        print("        Start Ollama with:  ollama serve")
        raise

    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Ollama generate API returned an error: {e}")
        print(f"        Make sure the model is pulled:  ollama pull {LLM_MODEL}")
        raise
