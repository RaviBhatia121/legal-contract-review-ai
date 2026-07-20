import type { DeploymentMode } from "../api/types";

export function DemoModeBadge({ mode }: { mode: DeploymentMode }) {
  if (mode !== "demo") return null;
  return (
    <span className="badge badge-demo" role="status">
      Demo mode — synthetic data only
    </span>
  );
}

// P7: persistent, non-dismissible hosted-demo banner. Carries the
// case-study narrative disclaimer (ADR-002/ADR-010): this hosted URL is a
// synthetic demo convenience only, never the production deployment target.
export function DemoModeBanner({ mode }: { mode: DeploymentMode }) {
  if (mode !== "demo") return null;
  return (
    <div className="demo-banner" role="status">
      <p>
        <strong>Demo mode — synthetic data only.</strong> Do not upload real, client,
        classified, export-controlled, or privileged documents to this hosted instance.
      </p>
      <p>
        This hosted URL is a synthetic demo convenience for the case study. It is not the
        target production architecture — the production deployment target is fully on-premises.
      </p>
    </div>
  );
}
