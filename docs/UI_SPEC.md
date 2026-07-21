# Part 2 UI Specification

## Product Shape
An intranet-style Legal Contract Risk Review portal. The interface is task-oriented and contains no chat transcript or message composer.

## Information Architecture
- `/`: Dashboard/home (P8.3) — review-history summary and recent reviews
- `/review/new`: upload and start review
- `/reviews/{id}`: processing status or completed findings
- `/admin/playbook`: read-only active playbook viewer
- `/admin/model`: runtime provider configuration
- Global: product name, Demo mode badge when active, synthetic-data warning, architecture/about link

**P7 hosted-demo presentation:** when `deployment_mode: demo`, the `Admin` and `Playbook`
nav links (and `/admin/model`/`/admin/playbook` screen content) are hidden — the hosted demo is
deterministic-only, so there is nothing to configure there, and `PUT
/config` is separately backend-locked in demo mode regardless
(`docs/API_CONTRACT.md`). A persistent, non-dismissible banner
(`DemoModeBanner`, `frontend/src/components/DemoModeBadge.tsx`) is shown
below the header carrying two messages: (1) synthetic-data-only /
no-real-document warning, and (2) the case-study narrative disclaimer —
this hosted URL is a synthetic demo convenience, not the production
on-prem deployment target. See `docs/SECURITY_EVIDENCE.md` section 10.

**P8.2 brand and shell:** the app shell (header, nav, footer) uses a
navy/gold visual language matching the Part 1/Part 3 case-study artifacts
(`frontend/src/index.css` CSS variables — `--navy`/`--gold`; risk colors and
the demo-mode warning palette are unchanged, since those are semantic, not
brand, colors). The favicon and header wordmark use a document/checkmark
glyph in place of the previous unrelated default scaffold mark; the unused
`frontend/public/icons.svg` scaffold leftover was deleted. `:focus-visible`
styles were added for keyboard navigation. The header wraps cleanly on
narrow viewports.

**P8.3 Dashboard/Home:** `/` now renders `Dashboard` (`frontend/src/pages/
Dashboard.tsx`) instead of redirecting to `/review/new`. `Dashboard` is the
first nav item, followed by `New review`, conditional `Playbook`, and conditional `Admin`; unlike
`Admin`, the `Dashboard` link is **not** hidden in demo mode (it has no
config/cloud implications and demo-mode review history is already labeled
synthetic-only by the persistent `DemoModeBanner`). The page fetches
`GET /api/v1/reviews?limit=50` once on mount (no auto-polling) and shows:
- A stat row: **Reviews shown** (always phrased "N (up to 50 most recently
  retained)" — never "Total reviews" or "All reviews", since P6's retention
  policy actively deletes older rows and the API caps at 50), Completed, In
  progress, Failed.
- Risk distribution (Critical/High/Medium/Low) among completed reviews only.
- Review mode split (AI-assisted vs. rules-only) among completed reviews only. Fallback
  reviews are counted as rules-only; the API still retains `fallback_used` and
  `fallback_reason`.
- Retrieval mode split (qdrant vs. degraded, completed only), one line.
- A Recent Reviews table (up to 10 most recent by `created_at`): document
  name, status, risk badge, completed date, a "View" link to
  `/reviews/{id}` with a per-row accessible name
  (`aria-label="View review for {document_name}"`) so multiple identical
  "View" link texts remain distinguishable to screen readers. The table
  scrolls horizontally within its own container on narrow viewports rather
  than causing page-wide overflow.
- An empty state ("No reviews yet. Start your first contract review.") when
  the fetched list is empty — not an error.
- **No fake ROI/time-saved/money-saved/risk-prevented metrics anywhere**,
  and no summed "total findings caught" headline stat either — that reads
  as an implied value pitch even though it would be real data, so it's
  deliberately excluded from the dashboard.

## Review Screen
- Drag/drop and browse control for one PDF or DOCX
- Allowed types, 15 MB limit, and 100-page processing limit shown before selection
- Selected document name and size
- Playbook name and version, read-only for the PoC
- Synthetic-data acknowledgement required in hosted Demo mode
- Primary action: `Review contract`
- Inline validation errors with safe remediation
- **P8.4 (Upload Screen Polish, implemented):** the screen now opens with a `New Legal
  Review` hero and one-line pipeline summary, a page-level "Active playbook" summary card
  (playbook id, version, rule count, the 8 required clause families in plain language, and a
  static "Produces:" line listing the finding output shape — deviation flags, missing
  clauses, risk labels, evidence, recommended actions), a 5-stage `workflow-strip`
  (Upload → Parse → Extract clauses → Apply playbook → Structured findings, shared with the
  Dashboard's workflow list), and a hosting-neutral trust note ("Processed on this server and
  never sent to a public AI service.") that deliberately avoids "on-premises"/"on-prem"/
  "air-gapped" since the same screen can run in hosted Demo mode. The playbook id/version
  line that previously lived inside `UploadForm` was removed in favor of the page-level card
  (`UploadForm` no longer takes a `playbookId` prop). Upload mechanics (drag/drop, browse,
  file-type/size validation, error handling, submit behavior, and the `Review contract`
  button and drag-and-drop label wording) are unchanged. No demo-mode acknowledgement
  checkbox was added — the existing global demo banner (`App.tsx`) already carries that
  disclosure; this remains a known, deferred UI item, not part of P8.4 scope.

## Processing Screen
- Client-side pre-job stages: uploading and validating file
- API-backed display stages: queued, parsing document, classifying clauses, checking playbook, extracting attributes, evaluating rules, validating result
- Display stages come from `current_stage`; persisted API status remains the broader state defined in `OUTPUT_SCHEMA.md`
- Current stage and elapsed time
- No simulated completion; poll the job endpoint
- Failure state with typed message, retry action, and the review ID for support reference

## Findings Screen
- Document name, detected source language, completion time, playbook version, and overall risk
- Summary counts by severity, missing clauses, and needs-review items
- Filter controls for severity, clause type, and finding type
- Default list shows Critical, High, Medium, and needs-review findings
- Each finding shows rule ID, clause/section, evidence, deviation, action, source, and confidence
- Missing clauses are visually distinct and never show invented evidence
- Low/compliant findings are collapsed by default
- Provenance drawer shows safe component/model versions and deployment mode
- If `provenance.fallback_used` is true, show a visible warning that the local AI model was
  unavailable and deterministic playbook fallback produced the review.
- **P8.5 (Findings Screen Polish, implemented):** the completed-review view now opens with a
  `Review result` page heading and a compliance banner ("Findings are decision support only,
  not legal advice. Final risk labels are assigned by the deterministic playbook rule engine.
  Supplemental guidance, when shown, is illustrative context only and does not change any
  finding's risk label."). The `SummaryPanel`'s severity counts are visually grouped under a
  "Findings by severity" label, with "Missing clauses" and "Needs review" set apart as a
  distinct callout row — same data, clearer hierarchy. The findings list (`FindingsList`)
  keeps its existing severity/clause-type/low-compliant filters and filtering logic
  unchanged, but now renders the filtered result grouped under severity subheadings
  (`Critical (n)`, `High (n)`, etc., only non-empty groups shown), with missing-clause
  findings broken out into their own `Missing clauses (n)` section below the severity
  groups rather than interleaved with deviation findings. Each finding card
  (`FindingCard`) now labels its evidence, reasoning, and recommendation blocks
  ("Evidence", "Why this is flagged", "Recommended action") — the underlying text is
  unchanged. The supplemental-guidance panel (P4) keeps its exact copy and disclaimer but
  gets a distinct bordered/tinted container so it reads as clearly separate from the
  finding's rule-derived content. No polling behavior, API calls, route path, schema,
  rule IDs, evidence/recommendation text, or guidance semantics changed.

## Admin Model Screen
**Implemented as of P5** (`frontend/src/pages/AdminModel.tsx`):
- Deployment mode: Local or Demo (read-only display)
- Provider catalog: Ollama, Anthropic, OpenAI, and Gemini, populated live from
  `GET /config/providers`
- Only implemented and server-allowlisted adapters are selectable and saveable — as of P5,
  only Docker-based Ollama (`_SAVEABLE_PROVIDERS = {"ollama"}` in `routes_config.py`); the
  selected hosted provider remains D-05 (still open), demonstrated only via the catalog/UI,
  not a working adapter
- Unimplemented catalog entries (Anthropic/OpenAI/Gemini) are shown as disabled `<option>`s
  labelled `(Not enabled)`; `PUT /config` independently rejects them server-side even if a
  client bypassed the disabled state
- Model name (editable text field)
- Base URL shown and editable only when `provider_type === "ollama"`; rejected by the server
  for any other provider, and rejected if malformed
- Credential field is a write-only password input, never pre-filled from `GET /config`;
  saved state displays only `Credential configured` via the placeholder
- In hosted Demo mode, an admin-entered credential is an in-memory override and the UI states
  that it clears on service restart
- Save action and Connection test action (`Test connection` button) with a visible
  success/failure result and latency, or the real rejection message on validation failure
- Visible statement that Docker Ollama/local is the PoC verification path and local inference is the target enterprise mode
- Visible warning that cloud-provider processing is for synthetic Demo data only
- **P8.6 (Admin Screen Polish, implemented):** `/admin/model` now presents the same
  configuration controls inside a clearer enterprise settings layout: a `Runtime Provider
  Configuration` heading, an explanatory lede that this is provider orchestration for the
  structured review pipeline (not a chatbot setting), a three-card posture summary
  (deterministic rule-engine authority, Docker Ollama/local runtime path, hosted-provider
  placeholders), a current-config summary card, a provider catalog with `Enabled`/`Not
  enabled` pills, and separate security/connection-test panels. The screen explicitly states
  that D-05 remains open and no cloud adapter is enabled by the UI. Credentials remain
  write-only and never pre-filled or displayed after save; `Test connection` is labelled as a
  reachability check only, not a review run. Demo-mode copy states that production
  configuration changes remain server-side locked and any admin-entered credential clears on
  service restart. Existing API calls and save/test behavior are unchanged.

## Admin Playbook Screen
**Implemented as P8.8** (`frontend/src/pages/AdminPlaybook.tsx`):
- Route: `/admin/playbook`
- Nav label: `Playbook`
- Hidden in hosted Demo mode with the rest of Admin/configuration navigation.
- Uses `GET /api/v1/playbooks/active`.
- Read-only view of the active `defense-services-v1` playbook.
- Shows playbook id, version, 27-rule count, 8 required clause-family count, severity
  coverage, required clause-family cards, missing-clause rule mappings, and the full rule
  table.
- Explicit read-only policy: CRUD is disabled in this PoC because playbook edits change risk
  decisions and require versioning, validation, audit trail, rollback, and explicit approval.
- No rule-engine, model, retrieval, upload, or review-result behavior changed.

## Architecture Screen
**Implemented as P9.1** (`frontend/src/pages/Architecture.tsx`):
- Route: `/architecture`
- Nav label: `Architecture`
- Visible in local and hosted Demo modes because it explains the target architecture and does not
  expose credentials or admin controls.
- Shows the Part 2 case-study stack explicitly: React/Vite frontend, FastAPI backend, Haystack
  orchestration, Ollama-compatible local/LAN model endpoint, Qdrant vector database, SQLite PoC
  storage, pypdf/python-docx parsing, and deterministic playbook rule authority.
- Includes the secure local data-flow walkthrough as a visual network flow: managed laptop ->
  office Wi-Fi or approved VPN -> internal portal -> upload -> validation -> local parsing ->
  clause extraction -> deterministic playbook evaluation -> structured findings, with public
  internet/unmanaged-device access shown as blocked.
- Shows Qdrant as an optional supplemental guidance branch that cannot change rule IDs,
  severity, or missing-clause output.
- Includes trust-boundary notes for server-side document handling, model calls, supplemental-only
  guidance, and write-only credentials.

## Drafting Support in Findings
**Implemented as P9.2** (`frontend/src/components/FindingCard.tsx`):
- Each finding can show a collapsed `Suggested approved clause language` panel.
- The panel uses `suggested_draft_clause` returned by the backend, which is deterministic
  approved-template language keyed by `rule_id`.
- Copy must keep the disclaimer: `Drafting support only; legal approval required before use.`
- This is not a chatbot, not redlining, and not free-form contract generation.

## Guidance Visibility
**Implemented as P9.3** (`frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/ReviewStatus.tsx`):
- Dashboard shows Qdrant guidance coverage as a real operating-mode card.
- Completed review pages show a `Supplemental guidance status` card:
  `Qdrant supplemental guidance active` or `Qdrant guidance unavailable`.
- The raw enum `degraded_full_rules` must never be shown to users.
- Copy must state that rule review is unaffected when Qdrant guidance is unavailable.

## Visual and Accessibility Rules
- Professional Legal/operations visual language, not a chatbot aesthetic.
- High and Critical findings are prominent, with text/icon labels in addition to color.
- Keyboard-accessible controls and visible focus states.
- Desktop-first but usable at mobile width.
- Evidence text remains readable and copyable.

## Empty and Error States
- No review: explain the three-step workflow.
- Unsupported/encrypted file: reject before job creation where possible.
- Provider unavailable: retain job failure information without exposing provider bodies.
- Expired review: explain retention and offer a new upload.
