import type { DocumentInfo, Provenance, ReviewSummary } from "../api/types";

interface Props {
  document: DocumentInfo;
  summary: ReviewSummary;
  provenance: Provenance;
}

// Correction: never surface the raw retrieval_mode enum value to users.
function retrievalLabel(provenance: Provenance): string {
  return provenance.retrieval_mode === "qdrant"
    ? "Supplemental guidance available"
    : "Guidance unavailable, rule review unaffected";
}

export function SummaryPanel({ document, summary, provenance }: Props) {
  return (
    <section className="summary-panel" aria-label="Review summary">
      <div className="summary-header">
        <h2>{document.name}</h2>
        <span className={`risk-badge risk-${summary.overall_risk.toLowerCase()}`}>
          Overall risk: {summary.overall_risk}
        </span>
      </div>
      <p className={`retrieval-status retrieval-${provenance.retrieval_mode}`}>{retrievalLabel(provenance)}</p>
      <dl className="summary-meta">
        <div>
          <dt>Language</dt>
          <dd>{document.language}</dd>
        </div>
        <div>
          <dt>Completed</dt>
          <dd>{new Date(provenance.completed_at).toLocaleString()}</dd>
        </div>
        <div>
          <dt>Playbook version</dt>
          <dd>{provenance.playbook_version}</dd>
        </div>
        <div>
          <dt>Clauses reviewed</dt>
          <dd>{summary.clauses_reviewed}</dd>
        </div>
      </dl>
      <ul className="summary-counts">
        <li>Critical: {summary.findings_by_risk.Critical}</li>
        <li>High: {summary.findings_by_risk.High}</li>
        <li>Medium: {summary.findings_by_risk.Medium}</li>
        <li>Low: {summary.findings_by_risk.Low}</li>
        <li>Missing clauses: {summary.missing_clause_count}</li>
        <li>Needs review: {summary.needs_review_count}</li>
      </ul>
    </section>
  );
}
