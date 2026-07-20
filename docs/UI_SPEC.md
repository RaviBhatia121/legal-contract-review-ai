# Part 2 UI Specification

## Product Shape
An intranet-style Legal Contract Risk Review portal. The interface is task-oriented and contains no chat transcript or message composer.

## Information Architecture
- `/review/new`: upload and start review
- `/reviews/{id}`: processing status or completed findings
- `/admin/model`: runtime provider configuration
- Global: product name, Demo mode badge when active, synthetic-data warning, architecture/about link

**P7 hosted-demo presentation:** when `deployment_mode: demo`, the `Admin`
nav link (and `/admin/model` screen content) is hidden — the hosted demo is
deterministic-only, so there is nothing to configure there, and `PUT
/config` is separately backend-locked in demo mode regardless
(`docs/API_CONTRACT.md`). A persistent, non-dismissible banner
(`DemoModeBanner`, `frontend/src/components/DemoModeBadge.tsx`) is shown
below the header carrying two messages: (1) synthetic-data-only /
no-real-document warning, and (2) the case-study narrative disclaimer —
this hosted URL is a synthetic demo convenience, not the production
on-prem deployment target. See `docs/SECURITY_EVIDENCE.md` section 10.

## Review Screen
- Drag/drop and browse control for one PDF or DOCX
- Allowed types, 15 MB limit, and 100-page processing limit shown before selection
- Selected document name and size
- Playbook name and version, read-only for the PoC
- Synthetic-data acknowledgement required in hosted Demo mode
- Primary action: `Review contract`
- Inline validation errors with safe remediation

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
