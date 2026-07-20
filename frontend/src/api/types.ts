export type ReviewStatus = "queued" | "parsing" | "analyzing" | "validating" | "completed" | "failed";
export type FindingType = "deviation" | "missing_clause" | "compliant" | "needs_review";
export type RiskLabel = "Low" | "Medium" | "High" | "Critical";
export type Source = "rule" | "model_assisted_rule";
export type DeploymentMode = "local" | "demo";
export type RetrievalMode = "qdrant" | "degraded_full_rules";
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
