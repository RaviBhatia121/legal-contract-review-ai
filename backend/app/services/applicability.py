"""Applicability checks.

WORKFLOW_SPEC.md requires rejecting documents with no usable text
(`NO_REVIEWABLE_TEXT`) and documents outside the services-agreement scope
(`DOCUMENT_NOT_APPLICABLE`).

`NO_REVIEWABLE_TEXT` is a text-length floor, checked immediately after
parsing (before any classification), and is unchanged since P1.

`DOCUMENT_NOT_APPLICABLE` was a provisional word-count heuristic through P2.
As of P3 it uses real classification output: applicable if at least
`MIN_APPLICABLE_CLAUSE_TYPES` distinct *required* clause types were
classified at or above the RULE_EVALUATION_SPEC.md confidence floor (0.60).
This runs the same way for both the P2 deterministic path and the P3
model-assisted path — `ClauseInput` is source-agnostic (see
`rule_engine.py`), so this check has no idea which one produced its input.
This is a real, source-agnostic upgrade, not a fixture-specific heuristic —
though its accuracy is still bounded by whatever produced the ClauseInputs
(deterministic mode inherits P2's fixture-oriented segmentation limits;
model mode inherits the classifier's actual accuracy).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.playbook.loader import Playbook
    from app.services.rule_engine import ClauseInput

MIN_REVIEWABLE_CHARS = 20
MIN_APPLICABLE_CLAUSE_TYPES = 2
CONFIDENCE_FLOOR = 0.60


def has_reviewable_text(text: str) -> bool:
    return len(text.strip()) >= MIN_REVIEWABLE_CHARS


def is_applicable(clause_inputs: "list[ClauseInput]", playbook: "Playbook") -> bool:
    accepted_required_types = {
        ci.clause_type
        for ci in clause_inputs
        if ci.clause_type in playbook.required_clause_types and ci.confidence >= CONFIDENCE_FLOOR
    }
    return len(accepted_required_types) >= MIN_APPLICABLE_CLAUSE_TYPES
