import type { Finding, GuidanceCategory } from "../api/types";

const CATEGORY_LABELS: Record<GuidanceCategory, string> = {
  negotiation_tip: "Negotiation tip",
  approved_example: "Approved example",
  playbook_reference: "Playbook reference",
};

function GuidancePanel({ guidance }: { guidance: Finding["guidance"] }) {
  if (guidance.length === 0) return null;
  return (
    <details className="guidance-panel">
      <summary>Supplemental guidance ({guidance.length})</summary>
      <p className="guidance-disclaimer">
        Illustrative decision-support content, not legal advice. Does not affect this finding's rule, severity, or risk.
      </p>
      <ul>
        {guidance.map((item) => (
          <li key={item.id}>
            <span className={`guidance-category guidance-${item.category}`}>
              {CATEGORY_LABELS[item.category]}
            </span>
            <p>{item.text}</p>
          </li>
        ))}
      </ul>
    </details>
  );
}

export function FindingCard({ finding }: { finding: Finding }) {
  const isMissing = finding.finding_type === "missing_clause";
  return (
    <article
      className={`finding-card risk-${finding.risk_label.toLowerCase()} ${isMissing ? "missing-clause" : ""}`}
      aria-label={`${finding.rule_id} finding`}
    >
      <header>
        <span className="rule-id">{finding.rule_id}</span>
        <span className="risk-label">{finding.risk_label}</span>
        {isMissing && <span className="missing-tag">Missing clause</span>}
      </header>
      {finding.title && <h3>{finding.title}</h3>}
      {finding.section_reference && <p className="section-ref">{finding.section_reference}</p>}
      {finding.evidence_text && (
        <blockquote className="evidence">{finding.evidence_text}</blockquote>
      )}
      {finding.deviation_reason && <p className="reason">{finding.deviation_reason}</p>}
      {finding.recommended_action && (
        <p className="action">
          <strong>Recommended action:</strong> {finding.recommended_action}
        </p>
      )}
      <footer>
        <span>Source: {finding.source}</span>
        {finding.classification_confidence != null && (
          <span>Confidence: {(finding.classification_confidence * 100).toFixed(0)}%</span>
        )}
        {finding.needs_review && <span className="needs-review-tag">Needs review</span>}
      </footer>
      <GuidancePanel guidance={finding.guidance} />
    </article>
  );
}
