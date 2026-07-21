import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiRequestError, listReviews } from "../api/client";
import type { ReviewSummaryItem } from "../api/types";

const IN_PROGRESS_STATUSES = ["queued", "parsing", "analyzing", "validating"] as const;
const RECENT_LIMIT = 10;
const FETCH_LIMIT = 50;

function isInProgress(status: ReviewSummaryItem["status"]): boolean {
  return (IN_PROGRESS_STATUSES as readonly string[]).includes(status);
}

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function Dashboard() {
  const [items, setItems] = useState<ReviewSummaryItem[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listReviews({ limit: FETCH_LIMIT })
      .then((data) => {
        if (cancelled) return;
        setItems(data.items);
        setLoadError(null);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiRequestError) {
          setLoadError(err.error.message);
        } else {
          setLoadError("Could not load review history.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loadError) {
    return (
      <div className="page dashboard">
        <h1>Dashboard</h1>
        <p className="form-error" role="alert">
          {loadError}
        </p>
        <Link to="/review/new">Start a new review</Link>
      </div>
    );
  }

  if (items === null) {
    return (
      <div className="page dashboard">
        <h1>Dashboard</h1>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  const completed = items.filter((item) => item.status === "completed");
  const inProgress = items.filter((item) => isInProgress(item.status));
  const failed = items.filter((item) => item.status === "failed");

  const riskCounts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
  for (const item of completed) {
    if (item.overall_risk) riskCounts[item.overall_risk] += 1;
  }

  const retrievalCounts = { qdrant: 0, degraded_full_rules: 0 };
  for (const item of completed) {
    retrievalCounts[item.retrieval_mode] += 1;
  }
  const modeCounts = { model: 0, rulesOnly: 0 };
  for (const item of completed) {
    if (!item.fallback_used && item.mode_used === "model") modeCounts.model += 1;
    else modeCounts.rulesOnly += 1;
  }

  const recent = [...items]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, RECENT_LIMIT);

  return (
    <div className="page dashboard">
      <h1>Defense Services Review Console</h1>
      <p className="lede">Structured contract risk review. No chatbot. No public AI upload.</p>
      <Link className="primary-action dashboard-cta" to="/review/new">
        New review
      </Link>

      {items.length === 0 ? (
        <p className="dashboard-empty">No reviews yet. Start your first contract review above.</p>
      ) : (
        <>
          <dl className="dashboard-stats" aria-label="Review history summary">
            <div>
              <dt>Reviews shown</dt>
              <dd>{items.length} (up to {FETCH_LIMIT} most recently retained)</dd>
            </div>
            <div>
              <dt>Completed</dt>
              <dd>{completed.length}</dd>
            </div>
            <div>
              <dt>In progress</dt>
              <dd>{inProgress.length}</dd>
            </div>
            <div>
              <dt>Failed</dt>
              <dd>{failed.length}</dd>
            </div>
          </dl>

          <ul className="summary-counts dashboard-risk-counts" aria-label="Risk distribution among completed reviews">
            <li>Critical: {riskCounts.Critical}</li>
            <li>High: {riskCounts.High}</li>
            <li>Medium: {riskCounts.Medium}</li>
            <li>Low: {riskCounts.Low}</li>
          </ul>

          {completed.length > 0 && (
            <div className="dashboard-ops-grid" aria-label="Review operating modes">
              <article>
                <span className="field-label">Review mode</span>
                <strong>{modeCounts.model} AI-assisted</strong>
                <p>{modeCounts.rulesOnly} rules-only fallback/review runs.</p>
              </article>
              <article>
                <span className="field-label">Qdrant guidance</span>
                <strong>{retrievalCounts.qdrant} with supplemental guidance</strong>
                <p>{retrievalCounts.degraded_full_rules} completed without guidance; rule review unaffected.</p>
              </article>
            </div>
          )}

          <h2>Recent reviews</h2>
          <div className="dashboard-table-wrap">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th scope="col">Document</th>
                  <th scope="col">Status</th>
                  <th scope="col">Risk</th>
                  <th scope="col">Completed</th>
                  <th scope="col">Mode</th>
                  <th scope="col">
                    <span className="sr-only">Action</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {recent.map((item) => (
                  <tr key={item.review_id}>
                    <td>{item.document_name}</td>
                    <td>{item.status}</td>
                    <td>
                      {item.overall_risk ? (
                        <span className={`risk-badge risk-${item.overall_risk.toLowerCase()}`}>
                          {item.overall_risk}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>{formatDate(item.completed_at)}</td>
                    <td>{!item.fallback_used && item.mode_used === "model" ? "AI-assisted" : "Rules only"}</td>
                    <td>
                      <Link to={`/reviews/${item.review_id}`} aria-label={`View review for ${item.document_name}`}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <h2>What this portal does</h2>
      <ol className="workflow-steps workflow-strip">
        <li>Upload a contract</li>
        <li>Extract clauses</li>
        <li>Apply the playbook</li>
        <li>Structured risks</li>
      </ol>
    </div>
  );
}
