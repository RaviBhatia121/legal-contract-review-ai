# Part 2 Case-Study Baseline

## Source
Source PDF retained outside repo at workspace root (`CASE STUDY - Head of Enterprise AI.pdf`), pages 1-2. Validated on 2026-07-18 by text extraction and visual inspection.

## Explicit Requirements
- Build a functional, working intranet portal prototype for one department from Part 1.
- Use an agentic, structured workflow rather than a generic chatbot.
- Focus on deterministic, pre-prompted AI actions.
- For Legal, support document upload and immediate structured, annotated risk points without chat.
- Specify and utilize an open-source, commercially viable model capable of running locally.
- Outline the full on-premises stack, including vector database, backend orchestration, and frontend portal.
- Provide access to a working prototype, such as a repository and hosted local demo link.
- Provide a brief walkthrough showing secure local data flow.

## Selected Interpretation
- Department: Legal.
- Workflow: contract upload -> clause extraction -> clause classification -> playbook comparison -> risk scoring -> structured findings.
- Primary output: annotated findings and missing-clause list.
- Target deployment: fully on-premises and capable of operating without external APIs.

## Prototype-Specific Additions
These choices support the demonstration but are not explicit case-study requirements:
- Defense-services contract playbook.
- Admin configuration screen.
- Provider-neutral model adapter.
- Hosted Demo mode using synthetic documents.

## Known Interpretation Risk
A hosted demo that processes documents only through a proprietary cloud model does not prove the requirement to utilize an open-source model capable of running locally. The hosted demo may use a cloud provider only as a disclosed convenience and only with synthetic data. Final prototype acceptance additionally requires at least one successful run of the same golden fixture through the pinned Docker Ollama/Qwen local path with runtime egress blocked; the evidence must record configuration, result, and observed variance.

## Scope Exclusions
- Contract drafting, despite being mentioned in the broader Part 1 Legal scope.
- Chat, question answering, redlining, negotiation, and electronic signature.
- HR and Procurement workflows.
- Production certification or handling of real defense information.
