"""Loads the machine-readable guidance corpus (`playbooks/guidance-<id>.json`).

Mirrors `app.playbook.loader`'s pattern: this module only parses and
validates the authored guidance content, it does not decide anything about
risk. Guidance is supplemental-only (ADR-004/D-09) — it is never consulted
by `app.services.rule_engine`.
"""

import json
import os
from dataclasses import dataclass
from functools import lru_cache

from app.core.config import get_settings
from app.playbook.loader import load_playbook

_ALLOWED_CATEGORIES = {"negotiation_tip", "approved_example", "playbook_reference"}


@dataclass(frozen=True)
class GuidanceItem:
    id: str
    rule_id: str
    clause_type: str
    category: str
    text: str
    source_note: str


@dataclass(frozen=True)
class GuidanceCorpus:
    guidance_id: str
    guidance_version: str
    playbook_id: str
    disclaimer: str
    items: tuple[GuidanceItem, ...]

    def items_for_rule(self, rule_id: str) -> tuple[GuidanceItem, ...]:
        return tuple(g for g in self.items if g.rule_id == rule_id)


class GuidanceLoadError(Exception):
    pass


@lru_cache
def load_guidance(guidance_id: str = "guidance-v1") -> GuidanceCorpus:
    settings = get_settings()
    path = os.path.join(settings.playbook_dir, f"{guidance_id}.json")
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError as exc:
        raise GuidanceLoadError(f"Guidance file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GuidanceLoadError(f"Guidance file is not valid JSON: {path}") from exc

    try:
        items = tuple(
            GuidanceItem(
                id=g["id"],
                rule_id=g["rule_id"],
                clause_type=g["clause_type"],
                category=g["category"],
                text=g["text"],
                source_note=g["source_note"],
            )
            for g in raw["items"]
        )
        corpus = GuidanceCorpus(
            guidance_id=raw["guidance_id"],
            guidance_version=raw["guidance_version"],
            playbook_id=raw["playbook_id"],
            disclaimer=raw["disclaimer"],
            items=items,
        )
    except KeyError as exc:
        raise GuidanceLoadError(f"Guidance file missing required field: {exc}") from exc

    _validate(corpus)
    return corpus


def _validate(corpus: GuidanceCorpus) -> None:
    ids = [g.id for g in corpus.items]
    if len(ids) != len(set(ids)):
        raise GuidanceLoadError("Duplicate guidance id values in corpus.")

    playbook = load_playbook(corpus.playbook_id)
    known_rule_ids = {r.rule_id for r in playbook.rules}
    for item in corpus.items:
        if item.rule_id not in known_rule_ids:
            raise GuidanceLoadError(
                f"Guidance {item.id} references unknown rule_id: {item.rule_id} "
                f"(not in playbook {corpus.playbook_id})"
            )
        if item.category not in _ALLOWED_CATEGORIES:
            raise GuidanceLoadError(f"Guidance {item.id} has invalid category: {item.category}")
        if item.clause_type not in playbook.clause_types:
            raise GuidanceLoadError(f"Guidance {item.id} references unknown clause_type: {item.clause_type}")
