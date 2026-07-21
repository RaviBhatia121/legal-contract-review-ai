# Part 2 API Contract

## Conventions
- Base path: `/api/v1`
- Content type: JSON except multipart upload
- Review processing: asynchronous job
- Identifiers: opaque UUIDs
- Errors: typed and free of document content or secrets

**P7 hosted-demo access:** when `deployment_mode: demo`, every endpoint
except `GET /health/live` requires HTTP Basic Auth (`DemoBasicAuthMiddleware`);
missing/incorrect credentials return `401` with a `WWW-Authenticate: Basic`
header, and the middleware fails closed (`503`) if the deployment has demo
mode on without configured access credentials. No-op in `local` mode. See
`docs/SECURITY_EVIDENCE.md` section 10.

## `POST /api/v1/reviews`
Create a review job.

Request:
- multipart field `file`: one PDF or DOCX
- multipart field `playbook_id`: defaults to `defense-services-v1`

Validation:
- maximum 15 MB, enforced twice as of P6: an early rejection based on the client-supplied
  `Content-Length` header (`MaxBodySizeMiddleware`, before the body is read into memory) plus
  the original post-read check, which stays authoritative since `Content-Length` can be
  omitted or misreported
- maximum 100 pages, enforced immediately after parsing and returned as `DOCUMENT_TOO_LONG`
- extension and detected MIME type must agree
- reject encrypted/password-protected files in the prototype
- sanitize display name and generate the storage path server-side

Response: `202 Accepted`

```json
{
  "review_id": "uuid",
  "status": "queued",
  "status_url": "/api/v1/reviews/uuid"
}
```

## `GET /api/v1/reviews`
Summary-only review history for the dashboard (P8.1). Never returns
`evidence_text`, full `findings`/`missing_clauses`, `parsed_text`, or any
model/credential internals.

Query parameters:
- `limit`: optional integer, default `20`, max `50` (`422` if exceeded).
- `offset`: optional integer, default `0`.

Response: `200 OK`

```json
{
  "items": [
    {
      "review_id": "uuid",
      "document_name": "sentinel-support-agreement.pdf",
      "status": "completed",
      "overall_risk": "Critical",
      "created_at": "2026-07-20T10:00:00Z",
      "completed_at": "2026-07-20T10:00:05Z",
      "findings_total": 8,
      "missing_clause_count": 1,
      "needs_review_count": 0,
      "deployment_mode": "local",
      "retrieval_mode": "degraded_full_rules",
      "mode_used": "deterministic",
      "fallback_used": false
    }
  ],
  "limit": 20,
  "offset": 0
}
```

Ordered by `created_at` descending. Includes reviews of any status; for a
non-completed review, `overall_risk`/`completed_at` are `null` and the
finding counts are `0`.

**Retention:** applies the same lazy delete-on-read policy as
`GET /reviews/{review_id}` (`app/services/retention.py`, shared by both
routes) — a terminal review past its retention window is deleted the moment
it's encountered on a list page and excluded from the response. **A
returned page may therefore contain fewer than `limit` items** when expired
rows were purged during that call; this is expected, not a bug. See
`docs/SECURITY_AND_DATA.md`'s PoC-retention note.

Aggregate counts (`findings_total`, `missing_clause_count`,
`needs_review_count`) are computed with one grouped aggregate query per
list call (not per-row), consistent for any page size up to `limit=50`.

## `GET /api/v1/reviews/{review_id}`
Return the in-progress, completed, or failed contract from `OUTPUT_SCHEMA.md`.

As of P9.2, completed finding objects may include:

```json
{
  "suggested_draft_clause": {
    "text": "Supplier shall process and store Customer Data only within Buyer-approved, client-controlled environments...",
    "source": "approved_template",
    "approval_note": "Drafting support only; legal approval required before use."
  }
}
```

Rules:
- deterministic approved-template support only; no free-form drafting endpoint exists
- keyed by `rule_id`, not generated from unrestricted user prompts
- does not affect risk scoring, rule IDs, missing-clause detection, or recommended actions

Response: `200 OK`, `404 Not Found`, or `410 Gone` after retention expiry.

**P6 implementation:** retention is enforced lazily, on this endpoint, not by a background
sweep. A completed/failed review past `Settings.retention_hours_local` (default 7 days) or
`retention_hours_demo` (default 24h, based on the review's own `deployment_mode`) is deleted
at the moment this endpoint is called for it, returning `410 REVIEW_EXPIRED`; a subsequent
call returns `404 REVIEW_NOT_FOUND`. An in-progress review is never expired regardless of
age. This is explicitly PoC-scale retention, not production records archival — see
`docs/SECURITY_EVIDENCE.md` §4.

## `DELETE /api/v1/reviews/{review_id}`
Delete the review, result, and temporary artifacts within prototype policy. As of P4, no
Qdrant-side deletion is needed: Qdrant stores only the static, admin-managed guidance corpus
(`playbooks/guidance-v1.json`, shared across every review), never per-review or
contract-derived data — retrieved guidance is a copy stored on the review's own
`Finding` rows in SQLite and is deleted with the review like any other field.

Response: `204 No Content`. Authorization is required in hosted mode.

## `GET /api/v1/config`
Return safe runtime configuration for the admin UI.

Hosted Demo mode requires admin authorization.

```json
{
  "deployment_mode": "local",
  "provider_type": "ollama",
  "model_name": "qwen3.6:35b",
  "base_url_display": "http://***.***.***.***:11434",
  "has_credential": false,
  "playbook_id": "defense-services-v1",
  "synthetic_data_only": false
}
```

Rules:
- never return an API key, secret fragment, or authorization header
- mask or omit a base URL when disclosure would expose internal topology

## `GET /api/v1/config/providers`
As of P5, returns the full provider catalog with each provider's implemented status, so the
admin UI can render Anthropic/OpenAI/Gemini as visibly disabled ("Not enabled") without
hardcoding the allowlist client-side.

```json
[
  { "provider_type": "anthropic", "implemented": false },
  { "provider_type": "gemini", "implemented": false },
  { "provider_type": "ollama", "implemented": true },
  { "provider_type": "openai", "implemented": false }
]
```

`implemented: true` is the only thing that determines whether a provider can be saved via
`PUT /config` — see that endpoint's rules below.

## `GET /api/v1/playbooks/active`
Returns the active playbook as a read-only, UI-safe view for the Admin Playbook screen
(P8.8). It does not expose file paths, loader internals, credentials, prompts, or document
content, and it does not allow playbook mutation.

```json
{
  "playbook_id": "defense-services-v1",
  "playbook_version": "1.0-draft",
  "editable": false,
  "edit_policy": "Read-only in this PoC. Playbook CRUD requires versioning, validation, audit trail, rollback, and explicit approval.",
  "required_clause_types": ["confidentiality", "data_handling"],
  "clause_families": [
    {
      "clause_type": "confidentiality",
      "required": true,
      "missing_clause_rule_id": "CONF-003",
      "rule_count": 3
    }
  ],
  "rules": [
    {
      "rule_id": "DATA-001",
      "area": "Data handling",
      "clause_type": "data_handling",
      "trigger": "Sensitive data may be processed or stored in external/public cloud or outside approved systems",
      "severity": "Critical",
      "recommended_action": "Restrict processing to approved client-controlled environments",
      "missing_clause_rule": false
    }
  ]
}
```

Rules:
- read-only only; no create/update/delete endpoint exists in this PoC
- return all 27 active rules and all 8 required clause families
- mark missing-clause rules with `missing_clause_rule: true`
- CRUD requires a later design for versioning, validation, audit trail, rollback, and explicit approval

## `PUT /api/v1/config`
Update allowed runtime configuration. Hosted mode requires admin authorization.

**P7 implementation:** unconditionally rejected with `CONFIGURATION_INVALID`
whenever `deployment_mode: demo`, regardless of payload — the hosted demo is
configured through Render environment variables, not browser edits. This is a backend lock,
independent of frontend navigation visibility; a direct API client cannot bypass it. See
`docs/SECURITY_EVIDENCE.md` section 10.

Rules:
- `provider_type` must be in the full catalog **and** currently implemented — as of P5, only
  `ollama` (`_SAVEABLE_PROVIDERS`); any other value is **rejected** with
  `CONFIGURATION_INVALID`, not silently accepted or ignored. This is a saveable-config
  restriction, separate from the display
  catalog above.
- `base_url` is **rejected**, not silently ignored, if the effective provider is not
  `ollama` — cloud-provider base URLs are fixed by backend code.
- Ollama `base_url` must be a valid `http://`/`https://` URL with a non-empty hostname; an
  invalid value is rejected with `CONFIGURATION_INVALID`. **P6 implementation**
  (`backend/app/services/ssrf_guard.py`): DNS-resolves the hostname and always rejects
  link-local/metadata/reserved/multicast/unspecified addresses; private RFC1918 ranges are
  allowed only when `deployment_mode: local` (rejected in demo mode); `localhost`,
  `127.0.0.1`, and the Docker Compose hostname `ollama` are always allowed. This is a
  blocklist for specific dangerous ranges, not a full enterprise egress-policy allowlist —
  see `docs/SECURITY_EVIDENCE.md` §1.
- an empty credential field preserves the existing credential
- credential values are write-only
- hosted-demo credential updates create an in-memory override that clears on process restart; environment-provided credentials remain the bootstrap source

## `POST /api/v1/config/test`
Test the saved provider without returning provider response bodies or secrets.

As of P3, this performs a real reachability check for `provider_type: ollama` (a `GET
/api/tags` ping against the configured base URL). Any other provider_type returns
`PROVIDER_UNAVAILABLE` honestly — no cloud adapter is implemented. As of
P5, the admin UI's "Test connection" button calls this endpoint directly and displays the
result. If the configured model is unavailable, the Admin UI explicitly says model-assisted
review is unavailable and reviews will use deterministic fallback until Ollama/model is
available.

Response:

```json
{
  "ok": true,
  "provider_type": "ollama",
  "model_name": "qwen3:4b",
  "latency_ms": 125
}
```

## `GET /api/v1/health/live`
Process liveness only. Does not contact model or data services.

## `GET /api/v1/health/ready`
Reports dependency readiness using booleans and safe labels, without credentials or topology details.

```json
{
  "status": "ok",
  "dependencies": {
    "database": true,
    "model_provider": "not_configured",
    "vector_store": "qdrant"
  }
}
```

As of P4, `dependencies.vector_store` is a real reachability check (`qdrant` if Qdrant
answers within a short internal timeout, `not_configured` otherwise) — not a hardcoded
placeholder. Retrieval is supplemental-only (ADR-004/D-09), so an unreachable/absent Qdrant
(the default Compose profile has none) never changes the top-level `status` or blocks
readiness for the rest of the app. As of P6, this check authenticates with
`Settings.qdrant_api_key` when one is configured (see `PUT /config`-adjacent Qdrant auth
notes in `docs/SECURITY_EVIDENCE.md` §5); unset behaves exactly as before.

## Error Envelope

```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Upload a PDF or DOCX file.",
    "retryable": false,
    "request_id": "opaque-id"
  }
}
```

## Initial Error Codes
- `UNSUPPORTED_FILE_TYPE`
- `FILE_TOO_LARGE`
- `ENCRYPTED_DOCUMENT`
- `DOCUMENT_TOO_LONG`
- `DOCUMENT_PARSE_FAILED`
- `NO_REVIEWABLE_TEXT`
- `DOCUMENT_NOT_APPLICABLE`
- `MODEL_TIMEOUT`
- `MODEL_OUTPUT_INVALID`
- `REVIEW_NOT_FOUND`
- `REVIEW_EXPIRED`
- `CONFIGURATION_INVALID`
- `PROVIDER_UNAVAILABLE`
- `JOB_INTERRUPTED`
- `INTERNAL_ERROR`
