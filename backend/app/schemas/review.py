from typing import Literal

from pydantic import BaseModel

SCHEMA_VERSION = "1.0-draft"

Status = Literal["queued", "parsing", "analyzing", "validating", "completed", "failed"]
FindingType = Literal["deviation", "missing_clause", "compliant", "needs_review"]
RiskLabel = Literal["Low", "Medium", "High", "Critical"]
Source = Literal["rule", "model_assisted_rule"]
DeploymentMode = Literal["local", "demo"]
RetrievalMode = Literal["qdrant", "degraded_full_rules"]
ReviewMode = Literal["deterministic", "model"]
GuidanceCategory = Literal["negotiation_tip", "approved_example", "playbook_reference"]


class DocumentInfo(BaseModel):
    name: str
    sha256: str
    page_count: int
    language: str


class FindingsByRisk(BaseModel):
    Critical: int
    High: int
    Medium: int
    Low: int


class ReviewSummary(BaseModel):
    overall_risk: RiskLabel
    clauses_reviewed: int
    findings_total: int
    findings_by_risk: FindingsByRisk
    missing_clause_count: int
    needs_review_count: int


class GuidanceItemOut(BaseModel):
    id: str
    text: str
    category: GuidanceCategory
    source_note: str
    score: float | None = None


class DraftClauseOut(BaseModel):
    text: str
    source: Literal["approved_template"] = "approved_template"
    approval_note: str


class FindingOut(BaseModel):
    finding_id: str
    finding_type: FindingType
    clause_id: str | None = None
    clause_type: str
    title: str | None = None
    section_reference: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    evidence_text: str | None = None
    classification_confidence: float | None = None
    risk_label: RiskLabel
    rule_id: str
    deviation_reason: str | None = None
    recommended_action: str | None = None
    needs_review: bool
    source: Source
    # P4: supplemental only — never influences rule_id/risk_label/severity.
    # Empty when retrieval is degraded (Qdrant/embedding unreachable) or when
    # this rule has no authored guidance yet.
    guidance: list[GuidanceItemOut] = []
    # P9.2: approved-template drafting support. This is deterministic,
    # template-backed clause language for Legal review, not free-form contract
    # generation and not legal advice.
    suggested_draft_clause: DraftClauseOut | None = None


class Provenance(BaseModel):
    deployment_mode: DeploymentMode
    department: str = "Legal"
    pipeline_version: str
    playbook_version: str
    prompt_version: str
    parser_name: str
    parser_version: str
    model_provider: str
    model_name: str
    model_revision: str | None = None
    mode_requested: ReviewMode
    mode_used: ReviewMode
    fallback_used: bool
    fallback_reason: str | None = None
    retrieval_mode: RetrievalMode
    completed_at: str


class ErrorOut(BaseModel):
    code: str
    message: str
    retryable: bool
    request_id: str | None = None


class ReviewCreated(BaseModel):
    review_id: str
    status: Literal["queued"]
    status_url: str


class ReviewSummaryItem(BaseModel):
    """P8.1 dashboard/history row — summary-only, never evidence_text, full
    findings, parsed_text, or model/credential internals."""

    review_id: str
    document_name: str
    status: Status
    overall_risk: RiskLabel | None = None
    created_at: str
    completed_at: str | None = None
    findings_total: int = 0
    missing_clause_count: int = 0
    needs_review_count: int = 0
    deployment_mode: DeploymentMode
    retrieval_mode: RetrievalMode
    mode_used: ReviewMode
    fallback_used: bool


class ReviewListOut(BaseModel):
    items: list[ReviewSummaryItem]
    limit: int
    offset: int


class ReviewOut(BaseModel):
    schema_version: str = SCHEMA_VERSION
    review_id: str
    document: DocumentInfo | None = None
    status: Status
    current_stage: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    review_summary: ReviewSummary | None = None
    findings: list[FindingOut] | None = None
    missing_clauses: list[FindingOut] | None = None
    provenance: Provenance | None = None
    error: ErrorOut | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorOut


class ConfigOut(BaseModel):
    deployment_mode: DeploymentMode
    provider_type: str
    model_name: str
    base_url_display: str
    has_credential: bool
    playbook_id: str
    synthetic_data_only: bool


class ConfigUpdate(BaseModel):
    provider_type: str | None = None
    model_name: str | None = None
    base_url: str | None = None
    credential: str | None = None


class ConfigTestResult(BaseModel):
    ok: bool
    provider_type: str
    model_name: str
    latency_ms: int


class ProviderInfo(BaseModel):
    provider_type: str
    implemented: bool


class PlaybookRuleOut(BaseModel):
    rule_id: str
    area: str
    clause_type: str
    trigger: str
    severity: RiskLabel
    recommended_action: str
    missing_clause_rule: bool


class PlaybookClauseFamilyOut(BaseModel):
    clause_type: str
    required: bool
    missing_clause_rule_id: str | None = None
    rule_count: int


class PlaybookOut(BaseModel):
    playbook_id: str
    playbook_version: str
    editable: bool = False
    edit_policy: str
    clause_types: list[str]
    required_clause_types: list[str]
    missing_clause_rule_by_type: dict[str, str]
    clause_families: list[PlaybookClauseFamilyOut]
    rules: list[PlaybookRuleOut]
