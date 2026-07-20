"""job_runner._attach_guidance tests — the critical proof that guidance
retrieval is pure post-processing enrichment and can never change a
finding's rule_id, risk_label, or any other risk-relevant field.

GuidanceService is faked at the class level (monkeypatched into
app.core.job_runner), the same pattern test_clause_intelligence.py uses to
bypass real HTTP for OllamaAdapter."""

import dataclasses
import json

import pytest

from app.core import job_runner
from app.core.config import get_settings
from app.db.models import Finding
from app.playbook.loader import load_playbook
from app.services.guidance_retrieval import DEGRADED_MODE, QDRANT_MODE, GuidanceResult
from app.services.rule_engine import FindingRecord

pytestmark = pytest.mark.asyncio


def _finding_record(rule_id: str) -> FindingRecord:
    return FindingRecord(
        finding_type="deviation",
        clause_key="data_handling:0",
        clause_type="data_handling",
        title="Data Handling",
        section_reference="Section 6",
        page_start=1,
        page_end=1,
        evidence_text="evidence",
        classification_confidence=0.9,
        risk_label="Critical",
        rule_id=rule_id,
        deviation_reason="reason",
        recommended_action="action",
        needs_review=False,
        source="rule",
    )


def _finding_row(record: FindingRecord) -> Finding:
    return Finding(
        finding_type=record.finding_type,
        clause_type=record.clause_type,
        title=record.title,
        section_reference=record.section_reference,
        page_start=record.page_start,
        page_end=record.page_end,
        evidence_text=record.evidence_text,
        classification_confidence=record.classification_confidence,
        risk_label=record.risk_label,
        rule_id=record.rule_id,
        deviation_reason=record.deviation_reason,
        recommended_action=record.recommended_action,
        needs_review=record.needs_review,
        source=record.source,
    )


def _risk_relevant_snapshot(row: Finding) -> dict:
    return {
        "finding_type": row.finding_type,
        "clause_type": row.clause_type,
        "risk_label": row.risk_label,
        "rule_id": row.rule_id,
        "deviation_reason": row.deviation_reason,
        "recommended_action": row.recommended_action,
        "needs_review": row.needs_review,
        "source": row.source,
    }


class _FakeGuidanceServiceWithResults:
    def __init__(self, settings):
        pass

    async def retrieve_for_rules(self, rules, limit=3):
        by_rule = {
            r.rule_id: [GuidanceResult(id="G-1", text="sample", category="negotiation_tip", source_note="note", score=0.9)]
            for r in rules
        }
        return by_rule, QDRANT_MODE


class _FakeGuidanceServiceDegraded:
    def __init__(self, settings):
        pass

    async def retrieve_for_rules(self, rules, limit=3):
        return {}, DEGRADED_MODE


async def test_attach_guidance_never_changes_risk_relevant_fields(monkeypatch):
    monkeypatch.setattr(job_runner, "GuidanceService", _FakeGuidanceServiceWithResults)
    playbook = load_playbook()

    record = _finding_record("DATA-001")
    row = _finding_row(record)
    before = _risk_relevant_snapshot(row)

    retrieval_mode = await job_runner._attach_guidance([row], [record], playbook, get_settings())

    after = _risk_relevant_snapshot(row)
    assert before == after, "guidance retrieval must never alter a risk-relevant field"
    assert retrieval_mode == QDRANT_MODE
    guidance = json.loads(row.guidance_json)
    assert len(guidance) == 1
    assert guidance[0]["id"] == "G-1"


async def test_attach_guidance_degrades_cleanly_without_failing(monkeypatch):
    monkeypatch.setattr(job_runner, "GuidanceService", _FakeGuidanceServiceDegraded)
    playbook = load_playbook()

    record = _finding_record("DATA-001")
    row = _finding_row(record)
    before = _risk_relevant_snapshot(row)

    retrieval_mode = await job_runner._attach_guidance([row], [record], playbook, get_settings())

    assert _risk_relevant_snapshot(row) == before
    assert retrieval_mode == DEGRADED_MODE
    assert json.loads(row.guidance_json) == []


async def test_attach_guidance_empty_findings_returns_degraded():
    playbook = load_playbook()
    retrieval_mode = await job_runner._attach_guidance([], [], playbook, get_settings())
    assert retrieval_mode == DEGRADED_MODE


async def test_attach_guidance_serializes_full_guidance_result(monkeypatch):
    monkeypatch.setattr(job_runner, "GuidanceService", _FakeGuidanceServiceWithResults)
    playbook = load_playbook()

    record = _finding_record("DATA-001")
    row = _finding_row(record)

    await job_runner._attach_guidance([row], [record], playbook, get_settings())

    guidance = json.loads(row.guidance_json)
    expected = dataclasses.asdict(
        GuidanceResult(id="G-1", text="sample", category="negotiation_tip", source_note="note", score=0.9)
    )
    assert guidance == [expected]
