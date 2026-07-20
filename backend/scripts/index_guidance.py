"""Embed and upsert playbooks/guidance-v1.json into Qdrant (P4).

Run inside the backend container, with the `retrieval` Compose profile up
and `qllama/multilingual-e5-small` pulled into Ollama:

    docker compose --profile retrieval up -d ollama qdrant
    docker compose exec ollama ollama pull qllama/multilingual-e5-small
    docker compose exec backend python scripts/index_guidance.py

Idempotent: (re)creates the collection each run, so it is safe to re-run
after editing playbooks/guidance-v1.json. Only authored guidance text is
embedded here — never contract content (see guidance_retrieval.py).

P6: if `PART2_QDRANT_API_KEY` is set (and the same key is set on the
`qdrant` Compose service via `QDRANT__SERVICE__API_KEY`), this script
authenticates with it. If unset, it connects unauthenticated — Qdrant's own
default, and the expected state whenever the `retrieval` profile is used
without deliberately enabling auth. The key itself is never printed or
logged, only whether one is configured.
"""

import asyncio
import sys

from qdrant_client import AsyncQdrantClient, models

from app.core.config import get_settings
from app.playbook.guidance_loader import load_guidance
from app.services.embedding_client import EmbeddingClient, EmbeddingUnavailableError

_EMBEDDING_DIM = 384  # qllama/multilingual-e5-small; verified in the P4 spike


async def main() -> None:
    settings = get_settings()
    print(f"Qdrant API key: {'configured' if settings.qdrant_api_key else 'not set (unauthenticated)'}")
    corpus = load_guidance(settings.guidance_id)
    embedder = EmbeddingClient(base_url=settings.ollama_base_url, model_name=settings.embedding_model)
    client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=settings.qdrant_timeout_s)

    try:
        await embedder.embed("connectivity check")
    except EmbeddingUnavailableError as exc:
        print(f"Embedding model unreachable at {settings.ollama_base_url}: {exc}", file=sys.stderr)
        print("Pull it first: docker compose exec ollama ollama pull " f"{settings.embedding_model}", file=sys.stderr)
        raise SystemExit(1) from exc

    if await client.collection_exists(settings.qdrant_collection):
        await client.delete_collection(settings.qdrant_collection)
    await client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=models.VectorParams(size=_EMBEDDING_DIM, distance=models.Distance.COSINE),
    )

    points = []
    for item in corpus.items:
        # "passage: " prefix matches e5's documented asymmetric query/passage
        # convention; retrieval queries use "query: " (see guidance_retrieval.py).
        vector = await embedder.embed(f"passage: {item.text}")
        points.append(
            models.PointStruct(
                # Qdrant point IDs must be an unsigned int or a UUID, not an
                # arbitrary string — derive a stable int from the guidance id
                # so re-running this script upserts (never duplicates) points.
                id=_stable_int_id(item.id),
                vector=vector,
                payload={
                    "id": item.id,
                    "rule_id": item.rule_id,
                    "clause_type": item.clause_type,
                    "category": item.category,
                    "text": item.text,
                    "source_note": item.source_note,
                },
            )
        )

    await client.upsert(collection_name=settings.qdrant_collection, points=points)
    print(f"Indexed {len(points)} guidance items into '{settings.qdrant_collection}' at {settings.qdrant_url}")


def _stable_int_id(guidance_id: str) -> int:
    import hashlib

    return int(hashlib.sha256(guidance_id.encode()).hexdigest()[:12], 16)


if __name__ == "__main__":
    asyncio.run(main())
