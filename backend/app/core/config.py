from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PART2_", env_file=".env")

    database_url: str = "sqlite+aiosqlite:///./part2.db"
    deployment_mode: str = "local"
    playbook_id: str = "defense-services-v1"
    max_upload_bytes: int = 15 * 1024 * 1024
    cors_allow_origins: list[str] = ["http://localhost:5173"]
    upload_temp_dir: str = "./upload_tmp"
    playbook_dir: str = "../playbooks"

    provider_type: str = "ollama"
    model_name: str = "qwen3.6:35b"
    base_url_display: str = "configured, hidden"

    # Non-Compose/local tests keep a deterministic default so CI does not need
    # a model server. Docker Compose overrides this to "model" and points to the
    # shared on-prem Ollama VM; rules-only remains the explicit fallback.
    clause_intelligence_mode: str = "deterministic"
    ollama_base_url: str = "http://ollama:11434"
    ollama_timeout_s: float = 60.0

    # P4: retrieval is always attempted (guidance is looked up via Qdrant,
    # never a plain in-process JSON lookup — see IMPLEMENTATION_PHASE_PLAN.md
    # P4 notes), but a review never fails because Qdrant is unreachable; it
    # degrades to retrieval_mode="degraded_full_rules" with guidance=[].
    # Retrieval never runs at all unless the `retrieval` Compose profile
    # started Qdrant — the default deterministic stack has nothing at this
    # URL to reach, which is the same degraded outcome as if Qdrant crashed.
    guidance_id: str = "guidance-v1"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "part2_guidance_v1"
    qdrant_timeout_s: float = 5.0
    embedding_model: str = "qllama/multilingual-e5-small"
    # P6: optional — Qdrant runs without auth (its default) when unset, which
    # is the expected/degraded state whenever the `retrieval` Compose
    # profile isn't running. Set on both the qdrant service and here to
    # enable authenticated access. Never logged; see SECURITY_EVIDENCE.md.
    qdrant_api_key: str | None = None

    @field_validator("qdrant_api_key", mode="before")
    @classmethod
    def _empty_qdrant_api_key_is_unset(cls, value: str | None) -> str | None:
        # docker-compose.yml always injects PART2_QDRANT_API_KEY (defaulting
        # to an empty string via ${QDRANT_API_KEY:-} when the host hasn't set
        # one) — normalize "" to None so downstream code's `if
        # settings.qdrant_api_key` check and qdrant-client's own
        # None-means-unauthenticated behavior both work as intended.
        return value or None

    # P6: PoC-only retention (see SECURITY_AND_DATA.md's "PoC retention, not
    # production archival" note) — a completed/failed review past this
    # window is lazily deleted the next time it is read (GET /reviews/{id}),
    # returning REVIEW_EXPIRED. No background sweep; matches SECURITY_AND_DATA.md's
    # documented defaults (7 days local, 24h hosted Demo mode).
    retention_hours_local: float = 24 * 7
    retention_hours_demo: float = 24

    # P7: hosted-demo access gate (DemoBasicAuthMiddleware). Only enforced
    # when deployment_mode == "demo"; unset/no-op in local mode. Set both via
    # platform env vars on the hosted deployment only — never committed, never
    # logged. If deployment_mode is "demo" but either is unset, the middleware
    # fails closed (rejects all requests) rather than serving the app
    # unauthenticated — see docs/SECURITY_EVIDENCE.md.
    demo_access_username: str | None = None
    demo_access_password: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
