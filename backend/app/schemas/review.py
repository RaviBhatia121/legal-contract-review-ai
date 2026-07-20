from typing import Literal

from pydantic import BaseModel

SCHEMA_VERSION = "1.0-draft"

Status = Literal["queued", "parsing", "analyzing", "validating", "completed", "failed"]
FindingType = Literal["deviation", "missing_clause", "compliant", "needs_review"]
RiskLabel = Literal["Low", "Medium", "High", "Critical"]
Source = Literal["rule", "model_assisted_rule"]
DeploymentMode = Literal["local", "demo"]
RetrievalMode = Literal["qdrant", "degraded_full_rules"]
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
