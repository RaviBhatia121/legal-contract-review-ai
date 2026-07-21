export type ReviewStatus = "queued" | "parsing" | "analyzing" | "validating" | "completed" | "failed";
export type FindingType = "deviation" | "missing_clause" | "compliant" | "needs_review";
export type RiskLabel = "Low" | "Medium" | "High" | "Critical";
export type Source = "rule" | "model_assisted_rule";
export type DeploymentMode = "local" | "demo";
export type RetrievalMode = "qdrant" | "degraded_full_rules";
export type ReviewMode = "deterministic" | "model";
export type GuidanceCategory = "negotiation_tip" | "approved_example" | "playbook_reference";

export interface DocumentInfo {
  name: string;
  sha256: string;
  page_count: number;
  language: string;
}

export interface FindingsByRisk {
  Critical: number;
  High: number;
  Medium: number;
  Low: number;
}

export interface ReviewSummary {
  overall_risk: RiskLabel;
  clauses_reviewed: number;
  findings_total: number;
  findings_by_risk: FindingsByRisk;
  missing_clause_count: number;
  needs_review_count: number;
}

export interface GuidanceItem {
  id: string;
  text: string;
  category: GuidanceCategory;
  source_note: string;
  score: number | null;
}

export interface DraftClause {
  text: string;
  source: "approved_template";
  approval_note: string;
}

export interface Finding {
  finding_id: string;
  finding_type: FindingType;
  clause_id: string | null;
  clause_type: string;
  title: string | null;
  section_reference: string | null;
  page_start: number | null;
  page_end: number | null;
  evidence_text: string | null;
  classification_confidence: number | null;
  risk_label: RiskLabel;
  rule_id: string;
  deviation_reason: string | null;
  recommended_action: string | null;
  needs_review: boolean;
  source: Source;
  // P4: supplemental only — never influences rule_id/risk_label/severity above.
  guidance: GuidanceItem[];
  // P9.2: approved-template drafting support only; legal approval remains required.
  suggested_draft_clause: DraftClause | null;
}

export interface Provenance {
  deployment_mode: DeploymentMode;
  department: string;
  pipeline_version: string;
  playbook_version: string;
  prompt_version: string;
  parser_name: string;
  parser_version: string;
  model_provider: string;
  model_name: string;
  model_revision: string | null;
  mode_requested: ReviewMode;
  mode_used: ReviewMode;
  fallback_used: boolean;
  fallback_reason: string | null;
  retrieval_mode: RetrievalMode;
  completed_at: string;
}

export interface ApiError {
  code: string;
  message: string;
  retryable: boolean;
  request_id?: string;
}

export interface ReviewResult {
  schema_version: string;
  review_id: string;
  document?: DocumentInfo;
  status: ReviewStatus;
  current_stage?: string | null;
  created_at?: string | null;
  started_at?: string | null;
  review_summary?: ReviewSummary;
  findings?: Finding[];
  missing_clauses?: Finding[];
  provenance?: Provenance;
  error?: ApiError;
}

export interface ReviewCreated {
  review_id: string;
  status: "queued";
  status_url: string;
}

// P8.3 dashboard/history — summary-only, mirrors backend ReviewSummaryItem.
export interface ReviewSummaryItem {
  review_id: string;
  document_name: string;
  status: ReviewStatus;
  overall_risk: RiskLabel | null;
  created_at: string;
  completed_at: string | null;
  findings_total: number;
  missing_clause_count: number;
  needs_review_count: number;
  deployment_mode: DeploymentMode;
  retrieval_mode: RetrievalMode;
  mode_used: ReviewMode;
  fallback_used: boolean;
}

export interface ReviewListOut {
  items: ReviewSummaryItem[];
  limit: number;
  offset: number;
}

export interface RuntimeConfig {
  deployment_mode: DeploymentMode;
  provider_type: string;
  model_name: string;
  base_url_display: string;
  has_credential: boolean;
  playbook_id: string;
  synthetic_data_only: boolean;
}

export interface ConfigUpdateRequest {
  provider_type?: string;
  model_name?: string;
  base_url?: string;
  credential?: string;
}

export interface ConfigTestResult {
  ok: boolean;
  provider_type: string;
  model_name: string;
  latency_ms: number;
}

export interface ProviderInfo {
  provider_type: string;
  implemented: boolean;
}

export interface PlaybookRule {
  rule_id: string;
  area: string;
  clause_type: string;
  trigger: string;
  severity: RiskLabel;
  recommended_action: string;
  missing_clause_rule: boolean;
}

export interface PlaybookClauseFamily {
  clause_type: string;
  required: boolean;
  missing_clause_rule_id: string | null;
  rule_count: number;
}

export interface Playbook {
  playbook_id: string;
  playbook_version: string;
  editable: boolean;
  edit_policy: string;
  clause_types: string[];
  required_clause_types: string[];
  missing_clause_rule_by_type: Record<string, string>;
  clause_families: PlaybookClauseFamily[];
  rules: PlaybookRule[];
}
