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

function DraftClausePanel({ draft }: { draft: Finding["suggested_draft_clause"] }) {
  if (!draft) return null;
  return (
    <details className="draft-clause-panel">
      <summary>Suggested approved clause language</summary>
      <p className="draft-disclaimer">{draft.approval_note}</p>
      <blockquote>{draft.text}</blockquote>
      <p className="hint">Source: {draft.source.replaceAll("_", " ")}</p>
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
        <div className="finding-field">
          <p className="field-label">Evidence</p>
          <blockquote className="evidence">{finding.evidence_text}</blockquote>
        </div>
      )}
      {finding.deviation_reason && (
        <div className="finding-field">
          <p className="field-label">Why this is flagged</p>
          <p className="reason">{finding.deviation_reason}</p>
        </div>
      )}
      {finding.recommended_action && (
        <div className="finding-field">
          <p className="field-label">Recommended action</p>
          <p className="action">{finding.recommended_action}</p>
        </div>
      )}
      <footer>
        <span>Source: {finding.source}</span>
        {finding.classification_confidence != null && (
          <span>Confidence: {(finding.classification_confidence * 100).toFixed(0)}%</span>
        )}
        {finding.needs_review && <span className="needs-review-tag">Needs review</span>}
      </footer>
      <DraftClausePanel draft={finding.suggested_draft_clause} />
      <GuidancePanel guidance={finding.guidance} />
    </article>
  );
}
