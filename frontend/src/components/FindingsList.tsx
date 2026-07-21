import { useMemo, useState } from "react";
import type { Finding, RiskLabel } from "../api/types";
import { FindingCard } from "./FindingCard";

interface Props {
  findings: Finding[];
  missingClauses: Finding[];
}

const ALL_RISKS: RiskLabel[] = ["Critical", "High", "Medium", "Low"];

export function FindingsList({ findings, missingClauses }: Props) {
  const all = useMemo(() => [...findings, ...missingClauses], [findings, missingClauses]);
  const clauseTypes = useMemo(() => Array.from(new Set(all.map((f) => f.clause_type))).sort(), [all]);

  const [riskFilter, setRiskFilter] = useState<Set<RiskLabel>>(new Set(ALL_RISKS));
  const [clauseTypeFilter, setClauseTypeFilter] = useState<string>("all");
  const [showLowCompliant, setShowLowCompliant] = useState(false);

  function toggleRisk(risk: RiskLabel) {
    setRiskFilter((prev) => {
      const next = new Set(prev);
      if (next.has(risk)) next.delete(risk);
      else next.add(risk);
      return next;
    });
  }

  const visible = all.filter((f) => {
    if (!riskFilter.has(f.risk_label)) return false;
    if (clauseTypeFilter !== "all" && f.clause_type !== clauseTypeFilter) return false;
    const isLowCompliant = f.risk_label === "Low" || f.finding_type === "compliant";
    if (isLowCompliant && !f.needs_review && !showLowCompliant) return false;
    return true;
  });

  const visibleDeviations = visible.filter((f) => f.finding_type !== "missing_clause");
  const visibleMissingClauses = visible.filter((f) => f.finding_type === "missing_clause");

  return (
    <section className="findings-list" aria-label="Findings">
      <div className="filters">
        <h2 className="filters-heading">Filters</h2>
        <fieldset>
          <legend>Severity</legend>
          {ALL_RISKS.map((risk) => (
            <label key={risk}>
              <input
                type="checkbox"
                checked={riskFilter.has(risk)}
                onChange={() => toggleRisk(risk)}
              />
              {risk}
            </label>
          ))}
        </fieldset>

        <label>
          Clause type
          <select value={clauseTypeFilter} onChange={(e) => setClauseTypeFilter(e.target.value)}>
            <option value="all">All</option>
            {clauseTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>

        <label>
          <input
            type="checkbox"
            checked={showLowCompliant}
            onChange={(e) => setShowLowCompliant(e.target.checked)}
          />
          Show Low / compliant findings
        </label>
      </div>

      {visible.length === 0 ? (
        <p className="no-findings">No findings match the current filters.</p>
      ) : (
        <>
          {ALL_RISKS.map((risk) => {
            const group = visibleDeviations.filter((f) => f.risk_label === risk);
            if (group.length === 0) return null;
            return (
              <div key={risk} className="severity-group" aria-label={`${risk} severity findings`}>
                <h2 className="severity-group-heading">
                  {risk} <span className="severity-group-count">({group.length})</span>
                </h2>
                <div className="finding-cards">
                  {group.map((finding) => (
                    <FindingCard key={finding.finding_id} finding={finding} />
                  ))}
                </div>
              </div>
            );
          })}

          {visibleMissingClauses.length > 0 && (
            <div className="missing-clauses-section" aria-label="Missing clauses">
              <h2 className="severity-group-heading">
                Missing clauses <span className="severity-group-count">({visibleMissingClauses.length})</span>
              </h2>
              <div className="finding-cards">
                {visibleMissingClauses.map((finding) => (
                  <FindingCard key={finding.finding_id} finding={finding} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
