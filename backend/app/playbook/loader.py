"""Loads the machine-readable playbook (`playbooks/<playbook_id>.json`).

The playbook is transcribed verbatim from DEFENSE_PLAYBOOK_TEMPLATE.md — this
module only parses and validates it, it does not encode rule logic itself.
Rule predicates live in `app.services.rule_engine`.
"""

import json
import os
from dataclasses import dataclass
from functools import lru_cache

from app.core.config import get_settings


@dataclass(frozen=True)
class Rule:
    rule_id: str
    area: str
    clause_type: str
    trigger: str
    severity: str
    recommended_action: str


@dataclass(frozen=True)
class Playbook:
    playbook_id: str
    playbook_version: str
    clause_types: tuple[str, ...]
    required_clause_types: tuple[str, ...]
    missing_clause_rule_by_type: dict[str, str]
    rules: tuple[Rule, ...]

    def rules_for_clause_type(self, clause_type: str) -> tuple[Rule, ...]:
        return tuple(r for r in self.rules if r.clause_type == clause_type)

    def rule_by_id(self, rule_id: str) -> Rule:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise KeyError(f"Unknown rule_id: {rule_id}")


class PlaybookLoadError(Exception):
    pass


@lru_cache
def load_playbook(playbook_id: str = "defense-services-v1") -> Playbook:
    settings = get_settings()
    path = os.path.join(settings.playbook_dir, f"{playbook_id}.json")
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError as exc:
        raise PlaybookLoadError(f"Playbook file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PlaybookLoadError(f"Playbook file is not valid JSON: {path}") from exc

    try:
        rules = tuple(
            Rule(
                rule_id=r["rule_id"],
                area=r["area"],
                clause_type=r["clause_type"],
                trigger=r["trigger"],
                severity=r["severity"],
                recommended_action=r["recommended_action"],
            )
            for r in raw["rules"]
        )
        playbook = Playbook(
            playbook_id=raw["playbook_id"],
            playbook_version=raw["playbook_version"],
            clause_types=tuple(raw["clause_types"]),
            required_clause_types=tuple(raw["required_clause_types"]),
            missing_clause_rule_by_type=dict(raw["missing_clause_rule_by_type"]),
            rules=rules,
        )
    except KeyError as exc:
        raise PlaybookLoadError(f"Playbook file missing required field: {exc}") from exc

    _validate(playbook)
    return playbook


def _validate(playbook: Playbook) -> None:
    rule_ids = [r.rule_id for r in playbook.rules]
    if len(rule_ids) != len(set(rule_ids)):
        raise PlaybookLoadError("Duplicate rule_id values in playbook.")
    for clause_type in playbook.required_clause_types:
        if clause_type not in playbook.missing_clause_rule_by_type:
            raise PlaybookLoadError(f"Required clause type missing a missing-clause rule mapping: {clause_type}")
    for rule in playbook.rules:
        if rule.clause_type not in playbook.clause_types:
            raise PlaybookLoadError(f"Rule {rule.rule_id} references unknown clause_type: {rule.clause_type}")
        if rule.severity not in ("Low", "Medium", "High", "Critical"):
            raise PlaybookLoadError(f"Rule {rule.rule_id} has invalid severity: {rule.severity}")
