import { useEffect, useMemo, useState } from "react";
import { ApiRequestError, getActivePlaybook } from "../api/client";
import type { Playbook, RiskLabel } from "../api/types";

const RISK_ORDER: RiskLabel[] = ["Critical", "High", "Medium", "Low"];

function formatClauseType(value: string) {
  return value.replaceAll("_", " ");
}

export function AdminPlaybook() {
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    getActivePlaybook()
      .then(setPlaybook)
      .catch((err) => {
        setLoadError(err instanceof ApiRequestError ? err.error.message : "Could not load active playbook.");
      });
  }, []);

  const severityCounts = useMemo(() => {
    const counts: Record<RiskLabel, number> = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    for (const rule of playbook?.rules ?? []) {
      counts[rule.severity] += 1;
    }
    return counts;
  }, [playbook]);

  if (loadError) {
    return (
      <div className="page admin-playbook">
        <h1>Active Playbook</h1>
        <p className="form-error" role="alert">
          {loadError}
        </p>
      </div>
    );
  }

  if (!playbook) {
    return (
      <div className="page admin-playbook">
        <h1>Active Playbook</h1>
        <p className="lede">Loading playbook...</p>
      </div>
    );
  }

  return (
    <div className="page admin-playbook">
      <h1>Active Playbook</h1>
      <p className="lede">
        Read-only view of the versioned Defense Services playbook used by the review pipeline. Editing is disabled in this
        PoC because playbook changes alter risk decisions.
      </p>

      <section className="playbook-overview-card" aria-label="Active playbook overview">
        <div>
          <span className="field-label">Playbook</span>
          <strong>{playbook.playbook_id}</strong>
        </div>
        <div>
          <span className="field-label">Version</span>
          <strong>{playbook.playbook_version}</strong>
        </div>
        <div>
          <span className="field-label">Rules</span>
          <strong>{playbook.rules.length}</strong>
        </div>
        <div>
          <span className="field-label">Required clause families</span>
          <strong>{playbook.required_clause_types.length}</strong>
        </div>
      </section>

      <p className="read-only-note">
        <strong>Read-only:</strong> {playbook.edit_policy}
      </p>

      <section className="playbook-section" aria-label="Rules by severity">
        <h2>Severity coverage</h2>
        <div className="severity-stat-grid">
          {RISK_ORDER.map((severity) => (
            <div key={severity} className={`severity-stat severity-${severity.toLowerCase()}`}>
              <span>{severity}</span>
              <strong>{severityCounts[severity]}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="playbook-section" aria-label="Required clause families">
        <h2>Required clause families</h2>
        <div className="clause-family-grid">
          {playbook.clause_families.map((family) => (
            <article key={family.clause_type} className="clause-family-card">
              <div>
                <h3>{formatClauseType(family.clause_type)}</h3>
                <p>{family.rule_count} rules</p>
              </div>
              <span className={family.required ? "status-pill enabled" : "status-pill neutral"}>
                {family.required ? "Required" : "Optional"}
              </span>
              {family.missing_clause_rule_id && (
                <p className="hint">Missing clause rule: {family.missing_clause_rule_id}</p>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="playbook-section" aria-label="Playbook rules">
        <div className="section-heading-row">
          <h2>Rule catalogue</h2>
          <p className="hint">Rules are evaluated by the deterministic playbook engine after clause extraction.</p>
        </div>
        <div className="playbook-rule-grid">
          {playbook.rules.map((rule) => (
            <article key={rule.rule_id} className="playbook-rule-card">
              <div className="playbook-rule-card-header">
                <div>
                  <strong>{rule.rule_id}</strong>
                  <span>{rule.area}</span>
                </div>
                <span className={`risk-badge risk-${rule.severity.toLowerCase()}`}>{rule.severity}</span>
              </div>
              <dl className="playbook-rule-fields">
                <div>
                  <dt>Clause type</dt>
                  <dd>{formatClauseType(rule.clause_type)}</dd>
                </div>
                <div>
                  <dt>Trigger</dt>
                  <dd>{rule.trigger}</dd>
                </div>
                <div>
                  <dt>Recommended action</dt>
                  <dd>{rule.recommended_action}</dd>
                </div>
              </dl>
              {rule.missing_clause_rule && <span className="rule-tag">Missing clause</span>}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
