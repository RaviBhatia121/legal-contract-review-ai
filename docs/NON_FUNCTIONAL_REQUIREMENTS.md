# Part 2 Non-Functional Requirements

## Security
- Synthetic data only in hosted Demo mode.
- No credentials or full document text in logs or frontend configuration payloads.
- Uploaded files are private to the review session and deleted according to retention settings.
- The application must start and function in local mode with external model and telemetry endpoints disabled.

## Performance Targets
- Accept files up to 15 MB and 100 pages for the prototype.
- Provisional objective: a 20-page digital-text contract should complete within 120 seconds in hosted Demo mode. This is not an acceptance gate until measured; the evidence must record host CPU, memory, accelerator if any, provider/model, and observed duration.
- UI status must update during processing and never appear frozen.
- API health responses should complete within 2 seconds.

## Reliability
- A failed stage returns a typed error and does not create a successful result.
- The same result identifier remains stable across refreshes.
- Re-running a document creates a new immutable review record.
- Temporary files are cleaned up after success, failure, or timeout.

## Auditability
- Every finding includes evidence, section/page reference when available, rule identifier, severity, and recommendation.
- Every review records component and configuration versions without recording secrets.
- The UI distinguishes model-derived extraction from deterministic rule evaluation.

## Accessibility and Usability
- Core workflow is keyboard accessible.
- Risk is communicated with text and iconography, not color alone.
- Tables remain usable on laptop and mobile-width displays.
- Errors state what failed and what the user can do next.

## Portability
- Runtime configuration uses environment variables or server-side secrets.
- Model providers implement one internal interface.
- Local deployment cannot depend on a cloud-only parser, vector database, or identity service.

## Language Handling
- Use UTF-8/Unicode-safe storage, APIs, logs, and UI rendering.
- Preserve original English or Indonesian evidence text without automatic translation.
- Prompts must analyze the source language and return structured enum values defined by the schema.
- Language-specific quality is evaluated separately; the English golden fixture remains the MVP gate.
