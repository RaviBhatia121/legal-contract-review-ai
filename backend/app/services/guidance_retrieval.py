"""Supplemental guidance retrieval (P4) — Qdrant-backed, post-processing only.

Guidance retrieval is a pure enrichment step called by `job_runner.py` after
`rule_engine.evaluate_clauses` has already produced final findings.
`rule_engine.py` itself is untouched by P4 and never imports this module —
guidance can never change a `rule_id`, `risk_label`, or `overall_risk`
(ADR-004/D-09).

Retrieval always goes through Qdrant — even a rule's single guidance item is
returned via a real Qdrant payload-filtered query, not an in-process JSON
dict lookup, so the vector database is genuinely exercised rather than
bypassed. A query embedding is computed via the local Ollama-served
`qllama/multilingual-e5-small` model (see `embedding_client.py`) and combined
with a `rule_id` payload filter, so results are ranked when a rule has
multiple candidate guidance items, while a query can never cross rule
boundaries and surface a different rule's guidance.

If Qdrant or the embedding model is unreachable, retrieval degrades to
`retrieval_mode="degraded_full_rules"` and `guidance=[]` on every finding.
This NEVER fails the review — same fail-closed-but-non-blocking pattern
P3 established for model-adapter errors, except retrieval failures don't
even raise; they return an empty result so the caller doesn't need a
try/except around every call site.
"""

from dataclasses import dataclass

from qdrant_client import AsyncQdrantClient, models

from app.core.config import Settings
from app.playbook.loader import Rule
from app.services.embedding_client import EmbeddingClient, EmbeddingUnavailableError

QDRANT_MODE = "qdrant"
DEGRADED_MODE = "degraded_full_rules"

_DEFAULT_LIMIT = 3

# Deliberately short and independent of Settings.qdrant_timeout_s (used for
# real retrieval calls): a health-check probe must fail fast when Qdrant is
# simply absent (the default profile), not block /health/ready for seconds.
_HEALTH_CHECK_TIMEOUT_S = 1.0


async def check_qdrant_reachable(settings: Settings, timeout_s: float = _HEALTH_CHECK_TIMEOUT_S) -> bool:
    """Lightweight reachability probe for GET /health/ready. Reveals no
    topology beyond a boolean — the caller decides what string to report."""
    try:
        client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=timeout_s)
        try:
            await client.get_collections()
            return True
        finally:
            await client.close()
    except Exception:
        return False


@dataclass(frozen=True)
class GuidanceResult:
    id: str
    text: str
    category: str
    source_note: str
    score: float | None


class GuidanceService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: AsyncQdrantClient | None = None
        self._embedder: EmbeddingClient | None = None

    def _get_client(self) -> AsyncQdrantClient:
        if self._client is None:
            # api_key is None whenever the retrieval profile isn't running
            # authenticated Qdrant (the default) — qdrant-client sends no
            # auth header in that case, matching Qdrant's own unauthenticated
            # default, so this degrades gracefully rather than requiring a
            # key to be set.
            self._client = AsyncQdrantClient(
                url=self._settings.qdrant_url,
                api_key=self._settings.qdrant_api_key,
                timeout=self._settings.qdrant_timeout_s,
            )
        return self._client

    def _get_embedder(self) -> EmbeddingClient:
        if self._embedder is None:
            self._embedder = EmbeddingClient(
                base_url=self._settings.ollama_base_url,
                model_name=self._settings.embedding_model,
                timeout_s=self._settings.qdrant_timeout_s,
            )
        return self._embedder

    async def retrieve_for_rules(
        self, rules: list[Rule], limit: int = _DEFAULT_LIMIT
    ) -> tuple[dict[str, list[GuidanceResult]], str]:
        """Returns (guidance_by_rule_id, retrieval_mode). Never raises."""
        unique_rules: dict[str, Rule] = {r.rule_id: r for r in rules}
        if not unique_rules:
            return {}, DEGRADED_MODE

        try:
            client = self._get_client()
            # Reachability probe up front: degrade the whole batch together
            # rather than partially populating some rules and not others.
            await client.get_collections()
        except Exception:
            return {}, DEGRADED_MODE

        guidance_by_rule: dict[str, list[GuidanceResult]] = {}
        for rule_id, rule in unique_rules.items():
            guidance_by_rule[rule_id] = await self._retrieve_one(client, rule, limit)
        return guidance_by_rule, QDRANT_MODE

    async def _retrieve_one(self, client: AsyncQdrantClient, rule: Rule, limit: int) -> list[GuidanceResult]:
        query_filter = models.Filter(
            must=[models.FieldCondition(key="rule_id", match=models.MatchValue(value=rule.rule_id))]
        )
        try:
            vector = await self._get_embedder().embed(f"query: {rule.trigger}")
            result = await client.query_points(
                collection_name=self._settings.qdrant_collection,
                query=vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            records = result.points
        except EmbeddingUnavailableError:
            # Embedding model unreachable but Qdrant itself answered the
            # reachability probe: fall back to an unranked payload-filtered
            # scroll — still a real Qdrant query, not a JSON lookup.
            try:
                records, _ = await client.scroll(
                    collection_name=self._settings.qdrant_collection,
                    scroll_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                )
            except Exception:
                return []
        except Exception:
            return []

        return [
            GuidanceResult(
                id=record.payload["id"],
                text=record.payload["text"],
                category=record.payload["category"],
                source_note=record.payload["source_note"],
                score=getattr(record, "score", None),
            )
            for record in records
        ]
