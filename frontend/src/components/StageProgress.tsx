import type { ReviewStatus } from "../api/types";

const STAGE_LABELS: Record<string, string> = {
  queued: "Queued",
  parsing_document: "Parsing document",
  checking_applicability: "Checking applicability",
  classifying_clauses: "Classifying clauses",
  checking_playbook: "Checking playbook",
  extracting_attributes: "Extracting attributes",
  evaluating_rules: "Evaluating rules",
  validating_result: "Validating result",
};

interface Props {
  status: ReviewStatus;
  currentStage: string | null | undefined;
  elapsedSeconds: number;
}

export function StageProgress({ status, currentStage, elapsedSeconds }: Props) {
  const label = currentStage ? STAGE_LABELS[currentStage] ?? currentStage : STAGE_LABELS[status] ?? status;
  return (
    <div className="stage-progress" role="status" aria-live="polite">
      <p className="stage-label">{label}...</p>
      <p className="stage-elapsed">Elapsed: {elapsedSeconds}s</p>
    </div>
  );
}
