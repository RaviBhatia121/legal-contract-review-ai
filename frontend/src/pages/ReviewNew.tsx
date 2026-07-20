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
      <h1>Start a contract review</h1>
      <ol className="workflow-steps">
        <li>Upload a PDF or DOCX contract.</li>
        <li>The system reviews it against the active playbook.</li>
        <li>Review structured findings and recommended actions.</li>
      </ol>
      <UploadForm
        playbookId={PLAYBOOK_ID}
        onSubmit={handleSubmit}
        submitting={submitting}
        errorMessage={errorMessage}
      />
    </div>
  );
}
