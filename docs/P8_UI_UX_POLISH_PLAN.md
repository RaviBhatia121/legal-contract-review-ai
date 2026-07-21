# P8 UI/UX and Demo Polish Plan

## Purpose
Define the incremental UI/UX polish phase for Part 2 after functional readiness was
confirmed. P8 must improve demo credibility and product clarity without changing the
contract-review rule engine, model adapters, retrieval logic, hosting status, or PDF/export
packaging.

## Status Key
- `pending`: not started
- `in_progress`: active implementation
- `blocked`: cannot proceed without a decision, dependency, or correction
- `complete`: implemented, verified, and documentation updated

## Current Status
P8 status: `complete` — P8.1-P8.8 complete. Hosting/live URL and PDF/export remain explicitly out of scope for P8.

## Scope
In scope:
- Product branding and intranet-style visual polish.
- Dashboard/home screen backed by real SQLite review data.
- Review history summary folded into the dashboard.
- Upload-screen explanation of the Defense Services Playbook and local processing.
- Findings-screen visual hierarchy and provenance readability.
- Admin-screen visual polish without adding cloud-provider claims.
- Read-only Admin Playbook visibility for the active Defense Services playbook.
- Tests and documentation updates for every implemented UI/API change.

Out of scope:
- Hosting/live public URL.
- PDF/export packaging.
- Chatbot or free-text assistant interface.
- Rule-engine, playbook, prompt, model-adapter, or retrieval behavior changes.
- Fake ROI, fake risk-reduction, fake usage metrics, or synthetic analytics not clearly
  labelled.
- Multi-user authentication, RBAC, or enterprise audit-accounting system.

## Non-Negotiable Guardrails
- Preserve the structured, non-chat workflow.
- Use real backend data for dashboard/history metrics.
- If any metric is illustrative, label it explicitly as illustrative; default preference is
  no illustrative metrics.
- Do not imply cloud providers are implemented. Anthropic/OpenAI/Gemini remain catalog-only
  and disabled until D-05 is explicitly accepted.
- Do not present SQLite review history as permanent enterprise records; respect retention
  language already documented in P6/P7.
- Do not change ports, Docker Compose project name, or default deterministic mode.

## Proposed Information Architecture
- `/`: Dashboard/home, replacing the current redirect to `/review/new`. **Implemented, P8.3.**
- `/review/new`: Enhanced upload flow.
- `/reviews/:reviewId`: Enhanced processing/findings view.
- `/admin/playbook`: Read-only active playbook viewer. **Implemented, P8.8.**
- `/admin/model`: Enhanced admin/provider configuration view.

No separate `/reviews` page in P8. Recent review history appears inside the dashboard to
keep navigation simple.

## Interface Sketches

### Dashboard / Home
```text
+--------------------------------------------------------------------------------+
| Legal Contract Risk Review                         Dashboard | New Review | Admin |
+--------------------------------------------------------------------------------+
| Defense Services Review Console                                                 |
| Structured contract risk review. No chatbot. No public AI upload.               |
|                                                                                |
| [Total Reviews] [Completed] [Critical/High Findings] [Retrieval Status]         |
|                                                                                |
| Recent Reviews                                                                  |
| +------------------------------+------------+----------+------------+---------+ |
| | Document                     | Status     | Risk     | Completed  | Action  | |
| | sentinel-support.pdf         | Completed  | Critical | Today      | View    | |
| | compliant-defense.pdf        | Completed  | Low      | Today      | View    | |
| +------------------------------+------------+----------+------------+---------+ |
|                                                                                |
| What this portal does                                                           |
| [Upload contract] -> [Extract clauses] -> [Apply playbook] -> [Structured risks] |
+--------------------------------------------------------------------------------+
```

### New Review
```text
+--------------------------------------------------------------------------------+
| New Legal Review                                                                |
| Upload one PDF/DOCX. The file is parsed locally and evaluated against the        |
| Defense Services Playbook.                                                      |
|                                                                                |
| Defense Services Playbook                                                       |
| Version: defense-services-v1 | 27 rules | 8 required clause families            |
| Checks: confidentiality, data handling, subcontracting, audit, IP, liability,    |
| termination, security incident obligations.                                      |
|                                                                                |
| [Drag/drop PDF or DOCX here]                                                     |
| Accepted: PDF/DOCX, 15 MB, 100 pages                                            |
|                                                                                |
| Decision support only; not legal advice. Use synthetic/demo documents only in    |
| hosted demo mode.                                                               |
|                                                                                |
| [Review Contract]                                                               |
+--------------------------------------------------------------------------------+
```

### Review Findings
```text
+--------------------------------------------------------------------------------+
| Review Result: sentinel-support-agreement.pdf                         Critical |
| Clauses reviewed: 7 | Findings: 8 | Missing clauses: 1 | Needs review: 0        |
|                                                                                |
| Severity Summary: [Critical 1] [High 5] [Medium 0] [Low 2]                     |
| Filters: Severity | Clause Type | Finding Type                                  |
|                                                                                |
| [Critical] DATA-001  Data Hosting                                               |
| Evidence: "Supplier may process Customer Data using regional public cloud..."   |
| Deviation: Processing outside approved client-controlled systems.               |
| Recommended action: Restrict processing to approved client-controlled systems.  |
| Guidance: supplemental negotiation tip, if retrieval is available.              |
|                                                                                |
| Missing Clauses                                                                 |
| [High] AUD-001 Audit / Inspection right missing                                 |
|                                                                                |
| How this review was generated                                                   |
| Parser: pypdf+python-docx | Playbook: 1.0-draft | Model: rule-engine/none      |
| Retrieval: degraded_full_rules | Deployment: local                              |
+--------------------------------------------------------------------------------+
```

### Admin / Model Configuration
```text
+--------------------------------------------------------------------------------+
| Runtime Configuration                                                           |
|                                                                                |
| Active provider                                                                 |
| [Ollama - enabled] Model: qwen3:4b Base URL: http://ollama:11434                |
|                                                                                |
| Provider catalog                                                                |
| [Ollama: enabled] [Anthropic: not enabled] [OpenAI: not enabled] [Gemini: not   |
| enabled]                                                                        |
|                                                                                |
| Local inference is the target enterprise mode. Hosted/cloud providers remain    |
| disabled until explicitly approved.                                             |
|                                                                                |
| [Save] [Test connection]                                                        |
+--------------------------------------------------------------------------------+
```

## Incremental Polish Phases

| Phase | Status | Technical Delivery | Feature Delivery | Exit Criteria |
|---|---|---|---|---|
| P8.1 Dashboard API | complete | Added `GET /api/v1/reviews` (declared before `GET /{review_id}`) + `ReviewRepository.list_summaries()` returning `list[tuple[Review, int, int, int]]`; retention logic shared via new `app/services/retention.py`; no schema change | Dashboard can use real review-history data | 9 new backend tests (empty list, ordering, limit/offset, limit-over-max, aggregate parity with single-GET, zeroed counts pre-completion, expired-review deletion, payload exclusions, demo-mode gating); 158/158 backend tests pass; live-verified against running Docker stack |
| P8.2 Brand and Shell | complete | Replaced favicon (document/checkmark glyph, was an unrelated default scaffold mark); deleted unused `frontend/public/icons.svg`; navy/gold CSS-variable palette (light + dark), `:focus-visible` styles, header/footer/nav shell polish, mobile header wrap. **Nav stays `New review` + conditional `Admin` — no `Dashboard` link added**, since that route is P8.3's; the shell is visually ready to receive it, but nothing points there yet | App no longer feels like default React scaffold | Frontend tests still pass (10/10); no route regressions; `/` still redirects to `/review/new`; verified visually in the browser preview (light + dark mode, desktop + mobile widths); demo-mode Admin-hiding logic untouched |
| P8.3 Dashboard/Home | complete | Added `/` dashboard route (`Dashboard.tsx`) using `GET /api/v1/reviews?limit=50`; added `Dashboard` nav link as the first nav item, not hidden in demo mode; `/` no longer redirects | User sees real instance-level review history (reviews shown, completed/in-progress/failed counts, risk distribution, retrieval split, recent-reviews table) with no fake ROI/value metrics | Empty, error, loading, and populated dashboard states covered by tests (7 new); root-route rendering and nav-visibility (local + demo mode) covered; live-verified against the running Docker stack's real review history (light/dark, desktop/mobile) |
| P8.4 Upload Screen Polish | complete | `ReviewNew.tsx` restyled: `New Legal Review` hero, page-level "Active playbook" summary card (id, version, 27 rules, 8 required clause families, "Produces:" output list), 5-stage `workflow-strip` (shared class with Dashboard, renamed from `dashboard-workflow`), hosting-neutral trust note. Removed the inline `.playbook-info` line and the now-unused `playbookId` prop from `UploadForm.tsx`; upload mechanics (drag/drop, browse, validation, error handling, submit) untouched | User understands the playbook, local/server-side processing, file limits, and expected output before upload, without any on-premises/hosting claim that could be false in demo mode | New `review-new.test.tsx` (5 tests: playbook card content, workflow strip, honest hosting-neutral wording with negative assertions against "on-premises"/"on-prem"/"air-gapped", no fake ROI/metrics wording, drag-and-drop label and `Review contract` button preserved); `golden-path.test.tsx` unchanged and still passing (22/22 frontend tests total); backend unaffected (158/158); live-verified in the running Docker stack (light/dark, desktop/mobile, no horizontal overflow) |
| P8.5 Findings Screen Polish | complete | Added `Review result` page heading and a compliance banner (decision-support/not-legal-advice, rule-engine-sourced risk, guidance doesn't affect risk scoring); `SummaryPanel` severity counts visually grouped, missing-clauses/needs-review set apart as a callout; `FindingsList` renders its existing filtered set grouped by severity subheadings with missing clauses in their own section; `FindingCard` adds Evidence/Why this is flagged/Recommended action field labels; guidance panel gets a distinct bordered container, copy unchanged | Results become executive-demo readable while preserving all structured fields and existing filter/polling behavior | Existing `golden-path.test.tsx` required no changes and still passes; new `findings-screen.test.tsx` (4 tests) covers the compliance banner, severity grouping, missing-clauses separation, and field-label/content preservation; full frontend suite 26/26; backend 158/158 unaffected; live-verified against a real completed review in the running Docker stack (light/dark, desktop/mobile, no horizontal overflow) |
| P8.6 Admin Screen Polish | complete | Restyled `AdminModel.tsx` into an enterprise runtime-provider configuration screen: posture cards, current-config summary, provider catalog cards/pills, runtime settings, security notes, and connection-test panel. Existing `GET /config`, `GET /config/providers`, `PUT /config`, and `POST /config/test` calls are unchanged | Admin screen demonstrates provider portability without overclaiming cloud support: Ollama is the only enabled provider, Anthropic/OpenAI/Gemini are visible as disabled placeholders, D-05 remains open, and no cloud adapter is implied as active | Admin tests expanded to 28/28 total: disabled providers remain disabled, credentials are write-only/never displayed, D-05/open-cloud-adapter wording is present, connection test is labelled as reachability-only, and demo-mode lock copy renders; frontend build clean; backend unchanged |
| P8.7 Documentation and Final Validation | complete | Reconciled P8 status docs and reran final validation | P8 is ready for user browser review | Backend tests 158/158 passed; frontend tests 28/28 passed; frontend build clean; Docker backend/frontend healthy on 8420/5420; live upload-to-findings smoke test completed with `overall_risk: Critical`, 7 findings, and 1 missing clause; docs reconciled |
| P8.8 Admin Playbook Viewer | complete | Added `GET /api/v1/playbooks/active` plus `/admin/playbook` read-only UI and local-mode nav link | User/admin can inspect the active Defense Services playbook, required clause families, severity coverage, missing-clause mappings, and all 27 rules without changing risk behavior | Backend tests 163/163 passed; frontend tests 33/33 passed; frontend build clean; endpoint verified live; no CRUD or rule/model/retrieval behavior change |

## Backend/API Contract Proposal

### `GET /api/v1/reviews`
Return review-history summaries only.

Query parameters:
- `limit`: optional integer, default `20`, max `50`.
- `offset`: optional integer, default `0`.

Response shape:
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
      "retrieval_mode": "degraded_full_rules"
    }
  ],
  "limit": 20,
  "offset": 0
}
```

Payload restrictions:
- Do not return `evidence_text`.
- Do not return full findings.
- Do not return credentials, prompts, hidden model output, or uploaded document text.

Retention requirements — **implemented, P8.1 complete**:
- The endpoint does not surface expired completed/failed reviews. Applies the same
  `retention_hours_local` / `retention_hours_demo` policy used by `GET /reviews/{id}`, via a
  shared `app/services/retention.py` helper (extracted from `routes_reviews.py`, no policy
  change).
- Delete-on-encounter (approved design choice): expired rows found on a page are deleted,
  matching `GET /{review_id}`'s existing lazy delete-on-read precedent, rather than merely
  filtered from the response. A returned page may therefore contain fewer than `limit` items
  when this happens — documented in `API_CONTRACT.md`.
- Backend test proving an expired review is both absent from the list response and actually
  deleted: `backend/tests/test_reviews_list.py::test_expired_review_is_absent_and_deleted`.

Query requirements:
- Derive `findings_total`, `missing_clause_count`, and `needs_review_count` from `Finding`
  rows through a single aggregate query per list call, not one query per review row.
- Keep the endpoint bounded (`limit` max 50) and ordered by `Review.created_at desc`.

## Real Dashboard Metrics Allowed
Allowed, because they can be computed from review rows:
- Reviews shown in the bounded list response, labelled as "up to 50 most recently retained";
  never "Total reviews" or "All reviews".
- Completed reviews within the bounded list response.
- Failed/in-progress counts.
- Overall-risk distribution for completed reviews.
- Recent reviews with status and risk.
- Retrieval mode distribution, if present on completed review provenance.

Not allowed unless explicitly labelled illustrative:
- Hours saved.
- Money saved.
- Risk reduction percentage.
- Legal cycle-time improvement.
- Enterprise-wide usage across teams.

## Documentation Update Enforcement
At the end of every P8 implementation subphase:
1. Read `MASTER_INDEX.md`.
2. Update `PLAN.md`, `AGENT_HANDOFF.md`, and this file.
3. If API changes, update `API_CONTRACT.md`, `OUTPUT_SCHEMA.md` if needed, and tests.
4. If UI behavior changes, update `UI_SPEC.md` and frontend tests.
5. If data model or retention behavior changes, update `DATA_MODEL.md` and
   `SECURITY_AND_DATA.md`.
6. If demo narrative changes, update `DEMO_RUNBOOK.md`.
7. Run relevant tests and record failures honestly.
8. Do not mark a P8 subphase complete unless code, tests, and docs agree.

## Reviewer Workflow
- Claude may implement after the plan is approved.
- Codex acts as reviewer/approver before each implementation batch is accepted.
- Any proposed deviation from this plan must be documented first and approved before code
  changes.

## Acceptance Gate for P8
P8 can be marked complete only when:
- `GET /api/v1/reviews` works and is tested, if implemented.
- Dashboard, upload, findings, and admin screens all render without regressions.
- Dashboard metrics are real or explicitly labelled illustrative.
- Favicon/default scaffold feel is removed.
- No chatbot UI is introduced.
- No cloud-provider implementation is implied.
- Backend tests pass.
- Frontend tests and build pass.
- Docker health check passes.
- One live upload-to-findings smoke test passes.
- Docs are reconciled.
