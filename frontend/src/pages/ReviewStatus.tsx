import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiRequestError, getReview } from "../api/client";
import type { ReviewResult } from "../api/types";
import { StageProgress } from "../components/StageProgress";
import { SummaryPanel } from "../components/SummaryPanel";
import { FindingsList } from "../components/FindingsList";

const POLL_INTERVAL_MS = 1500;

export function ReviewStatus() {
  const { reviewId } = useParams<{ reviewId: string }>();
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const startedRef = useRef<number>(Date.now());

  useEffect(() => {
    if (!reviewId) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const data = await getReview(reviewId!);
        if (cancelled) return;
        setResult(data);
        setLoadError(null);
        if (data.status !== "completed" && data.status !== "failed") {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiRequestError) {
          setLoadError(err.error.message);
        } else {
          setLoadError("Could not load this review.");
        }
      }
    }

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [reviewId]);

  useEffect(() => {
    if (!result || result.status === "completed" || result.status === "failed") return;
    const tick = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedRef.current) / 1000));
    }, 1000);
    return () => clearInterval(tick);
  }, [result]);

  if (loadError) {
    return (
      <div className="page review-status">
        <p className="form-error" role="alert">
          {loadError}
        </p>
        <p>Review ID: {reviewId}</p>
        <Link to="/review/new">Start a new review</Link>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="page review-status">
        <p>Loading review...</p>
      </div>
    );
  }

  if (result.status === "failed") {
    return (
      <div className="page review-status">
        <h1>Review failed</h1>
        <p className="form-error" role="alert">
          {result.error?.message ?? "The review could not be completed."}
        </p>
        <p>Review ID: {result.review_id}</p>
        <Link to="/review/new">Start a new review</Link>
      </div>
    );
  }

  if (result.status !== "completed") {
    return (
      <div className="page review-status">
        <h1>Reviewing contract</h1>
        <StageProgress status={result.status} currentStage={result.current_stage} elapsedSeconds={elapsedSeconds} />
        <p>Review ID: {result.review_id}</p>
      </div>
    );
  }

  return (
    <div className="page review-findings">
      {result.document && result.review_summary && result.provenance && (
        <SummaryPanel document={result.document} summary={result.review_summary} provenance={result.provenance} />
      )}
      <FindingsList findings={result.findings ?? []} missingClauses={result.missing_clauses ?? []} />
    </div>
  );
}
