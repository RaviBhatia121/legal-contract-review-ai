"""Local embedding client (P4) — calls Ollama's `/api/embeddings` endpoint.

Reuses the same Docker-based Ollama runtime P3's `OllamaAdapter` uses, just a
different model (an embedding model, not a chat/completion model). See
TECH_STACK_AND_LICENSES.md's P4 spike notes for why
`qllama/multilingual-e5-small` — a community GGUF quantization of the
MIT-licensed `intfloat/multilingual-e5-small` accepted in ADR-005/D-04 — was
selected: it is the model that is actually servable through this project's
existing Docker Ollama infrastructure, verified end to end (384-dim,
deterministic output) before being adopted.
"""

import httpx


class EmbeddingUnavailableError(Exception):
    """Raised when the embedding model cannot be reached or returns invalid output."""


class EmbeddingClient:
    def __init__(self, base_url: str, model_name: str, timeout_s: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_s = timeout_s

    async def embed(self, text: str) -> list[float]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                )
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingUnavailableError(f"Embedding request failed: {exc}") from exc

        envelope = resp.json()
        embedding = envelope.get("embedding")
        if not embedding:
            raise EmbeddingUnavailableError("Embedding response missing 'embedding' field")
        return embedding
