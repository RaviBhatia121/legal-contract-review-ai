# AI Model Fallback Appendix

## Decision
Part 2 must demonstrate an AI-enabled legal review system, not only a deterministic rules
demo. The active demo model path is the shared on-prem Ollama VM
(`http://<ollama-vm-ip>:11434`) with `qwen3.6:35b`; deterministic rule evaluation remains
the safety authority and fallback.

## Runtime Behavior
- Local Docker demo review mode defaults to model-assisted through the shared Ollama VM.
- The laptop-local Ollama container is opt-in only (`--profile local-model`) and is not
  started by the default Compose stack.
- When `PART2_CLAUSE_INTELLIGENCE_MODE=model` is enabled, the backend attempts model-assisted
  clause classification/extraction through Ollama.
- If the model path is unavailable, times out, or returns invalid structured output, the
  review completes through deterministic playbook rules.
- This fallback is disclosed in API provenance and the UI.
- The Ollama adapter strips Qwen-style thinking/prose before validation so valid JSON
  answers are not rejected merely because the model prepended reasoning text.

## Disclosure Fields
- `provenance.mode_requested`: `deterministic | model`
- `provenance.mode_used`: `deterministic | model`
- `provenance.fallback_used`: `true | false`
- `provenance.fallback_reason`: model-path exception class when fallback was used

## UI Disclosure
The findings screen shows a visible warning when fallback is used:

> Local AI model unavailable. This review used deterministic playbook rules only. No
> model-assisted clause classification was applied.

The dashboard labels completed reviews as `AI-assisted` or `Rules only`; fallback reviews are
included in `Rules only` and retain detailed fallback provenance in the API.

## Why This Exists
This keeps the proof-of-concept honest for the case study: model capability is present and
testable, but if the local model runtime is unavailable, the user can still review the
contract using deterministic playbook rules with clear disclosure.
