from fastapi import APIRouter

from app.core.config import get_settings
from app.playbook.loader import load_playbook
from app.schemas.review import PlaybookClauseFamilyOut, PlaybookOut, PlaybookRuleOut

router = APIRouter(prefix="/api/v1/playbooks", tags=["playbooks"])


@router.get("/active", response_model=PlaybookOut)
async def get_active_playbook() -> PlaybookOut:
    """Return the active playbook as a read-only, UI-safe view.

    CRUD is deliberately out of scope for the PoC because playbook edits change
    risk decisions and need versioning, validation, audit, and rollback.
    """
    settings = get_settings()
    playbook = load_playbook(settings.playbook_id)
    missing_rule_ids = set(playbook.missing_clause_rule_by_type.values())

    clause_families = [
        PlaybookClauseFamilyOut(
            clause_type=clause_type,
            required=clause_type in playbook.required_clause_types,
            missing_clause_rule_id=playbook.missing_clause_rule_by_type.get(clause_type),
            rule_count=len(playbook.rules_for_clause_type(clause_type)),
        )
        for clause_type in playbook.clause_types
        if clause_type != "unknown"
    ]

    rules = [
        PlaybookRuleOut(
            rule_id=rule.rule_id,
            area=rule.area,
            clause_type=rule.clause_type,
            trigger=rule.trigger,
            severity=rule.severity,  # type: ignore[arg-type]
            recommended_action=rule.recommended_action,
            missing_clause_rule=rule.rule_id in missing_rule_ids,
        )
        for rule in playbook.rules
    ]

    return PlaybookOut(
        playbook_id=playbook.playbook_id,
        playbook_version=playbook.playbook_version,
        edit_policy="Read-only in this PoC. Playbook CRUD requires versioning, validation, audit trail, rollback, and explicit approval.",
        clause_types=list(playbook.clause_types),
        required_clause_types=list(playbook.required_clause_types),
        missing_clause_rule_by_type=playbook.missing_clause_rule_by_type,
        clause_families=clause_families,
        rules=rules,
    )
