import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiRequestError, createReview } from "../api/client";
import { UploadForm } from "../components/UploadForm";

const PLAYBOOK_ID = "defense-services-v1";

export function ReviewNew() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(file: File) {
    setSubmitting(true);
    setErrorMessage(null);
    try {
      const created = await createReview(file, PLAYBOOK_ID);
      navigate(`/reviews/${created.review_id}`);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setErrorMessage(err.error.message);
      } else {
        setErrorMessage("The review could not be started. Try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page review-new">
      <h1>New Legal Review</h1>
      <p className="lede">
        Upload one contract. It is parsed and evaluated on this server against the Defense
        Services playbook, then returned as structured, evidence-linked findings.
      </p>

      <div className="playbook-card" role="region" aria-label="Active playbook summary">
        <h2>Active playbook</h2>
        <dl>
          <div>
            <dt>Playbook</dt>
            <dd>{PLAYBOOK_ID}</dd>
          </div>
          <div>
            <dt>Version</dt>
            <dd>1.0-draft</dd>
          </div>
          <div>
            <dt>Rules</dt>
            <dd>27</dd>
          </div>
        </dl>
        <p className="playbook-card-label">Checks for required clauses covering:</p>
        <ul className="playbook-clause-list">
          <li>Confidentiality</li>
          <li>Data handling</li>
          <li>Subcontracting</li>
          <li>Audit and inspection</li>
          <li>Intellectual property</li>
          <li>Liability and indemnity</li>
          <li>Termination and exit</li>
          <li>Security incident response</li>
        </ul>
        <p className="playbook-card-label">Produces:</p>
        <p>Clause deviation flags, missing-clause findings, risk labels, cited evidence, and recommended actions.</p>
      </div>

      <ol className="workflow-steps workflow-strip">
        <li>Upload</li>
        <li>Parse</li>
        <li>Extract clauses</li>
        <li>Apply playbook</li>
        <li>Structured findings</li>
      </ol>

      <p className="hint trust-note">
        Processed on this server and never sent to a public AI service.
      </p>

      <UploadForm onSubmit={handleSubmit} submitting={submitting} errorMessage={errorMessage} />
    </div>
  );
}
