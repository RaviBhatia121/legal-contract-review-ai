# Part 2 Requirements

## Case Study Interpretation
Part 2 requires a functional, working intranet portal proof of concept for the Legal department. The authoritative transcription and interpretation are in `CASE_STUDY_BASELINE.md`.
The prototype must be:
- Agentic
- Structured
- Non-chatbot
- Deterministic and pre-prompted in workflow structure
- Demonstrable through a working intranet portal and accessible repository/demo
- Built around open-source, commercially viable models capable of local execution
- Explainable as a fully on-premises stack, including vector database, backend orchestration, and frontend

## Exact Demo Behavior
The user should be able to:
1. Upload a legal contract.
2. Run a deterministic review pipeline.
3. See extracted clauses.
4. See risk classifications.
5. See deviations from the playbook.
6. See a structured results view.

## Language and Document Boundary
- Golden acceptance fixture: English, digitally generated PDF and DOCX.
- Architecture: Unicode-safe and language-neutral; Indonesian text must be preserved without corruption.
- Stretch verification: one synthetic Indonesian digital-text smoke test if schedule permits.
- No multilingual production-quality claim without a bilingual playbook and Indonesian legal/model evaluation.
- Image-only/scanned-document OCR quality is outside the two-day acceptance gate.

## Non-Negotiables
- No chatbot-style conversation as the primary interaction.
- No free-form answer as the primary output.
- No expansion beyond the Legal workflow for Part 2.
- No deviation from the structured output requirement.
- No cloud-only dependency in the target enterprise architecture.
- No real sensitive or defense-sector data in a hosted demo.
- No claim that the prototype provides legal advice or production certification.

## Demo Narrative
The prototype should show:
- A clear upload flow
- A visible processing pipeline
- A structured findings screen
- An admin/configuration area to support enterprise deployment confidence

## Acceptance Criteria
The Part 2 prototype is ready only when:
- The workflow is complete end to end.
- The output matches the defined schema.
- The UI presents findings clearly.
- The solution can be explained in one short architecture walkthrough.
- Every finding provides evidence, a playbook rule, severity, and recommended action.
- The pinned Docker Ollama/Qwen path successfully processes the golden fixture with runtime egress blocked before final delivery; a cloud or fixed-result run cannot substitute for this evidence.
- Hosted-demo exceptions are clearly labelled and do not change the on-premises target design.
