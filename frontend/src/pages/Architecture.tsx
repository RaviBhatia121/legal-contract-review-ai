import { useEffect, useState } from "react";
import { ApiRequestError, getConfig } from "../api/client";
import type { RuntimeConfig } from "../api/types";

const STACK_ITEMS = [
  {
    label: "Frontend portal",
    value: "React + Vite",
    detail: "Upload, dashboard, findings, admin configuration, playbook visibility.",
  },
  {
    label: "Backend API",
    value: "FastAPI",
    detail: "File validation, job orchestration, parsing, review APIs, retention controls.",
  },
  {
    label: "Orchestration",
    value: "Haystack 2.x pipeline",
    detail: "Structured model-assisted clause classification and attribute extraction.",
  },
  {
    label: "Model runtime",
    value: "Ollama-compatible local endpoint",
    detail: "Open-source, commercially viable local/LAN model path; no public AI API required.",
  },
  {
    label: "Vector database",
    value: "Qdrant",
    detail: "Supplemental playbook guidance retrieval only; risk decisions stay rule-based.",
  },
  {
    label: "PoC storage",
    value: "SQLite",
    detail: "Local prototype metadata store with retention cleanup; not production archival.",
  },
  {
    label: "Document parsing",
    value: "pypdf + python-docx",
    detail: "Local text extraction for digital PDF/DOCX files without hosted parsing APIs.",
  },
  {
    label: "Risk authority",
    value: "Deterministic playbook engine",
    detail: "Final rule IDs, severity, missing clauses, and recommended actions come from the playbook.",
  },
];

export function Architecture() {
  const [config, setConfig] = useState<RuntimeConfig | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    getConfig()
      .then((loaded) => {
        setConfig(loaded);
        setLoadError(null);
      })
      .catch((err) => {
        setLoadError(err instanceof ApiRequestError ? err.error.message : "Could not load runtime configuration.");
      });
  }, []);

  return (
    <div className="page architecture-page">
      <h1>Architecture and Data Flow</h1>
      <p className="lede">
        Brief walkthrough of the local-first stack used by this Legal contract-review prototype. The portal is a
        structured workflow, not a chatbot, and the deterministic playbook remains the final risk authority.
      </p>

      {loadError && (
        <p className="form-error" role="alert">
          {loadError}
        </p>
      )}

      <section className="architecture-current-card" aria-label="Current model path">
        <div>
          <span className="field-label">Configured provider</span>
          <strong>{config?.provider_type ?? "Loading..."}</strong>
        </div>
        <div>
          <span className="field-label">Configured model</span>
          <strong>{config?.model_name ?? "Loading..."}</strong>
        </div>
        <div>
          <span className="field-label">Endpoint pattern</span>
          <strong>{config?.base_url_display ?? "Loading..."}</strong>
        </div>
        <div>
          <span className="field-label">Playbook</span>
          <strong>{config?.playbook_id ?? "Loading..."}</strong>
        </div>
      </section>

      <section className="architecture-section" aria-label="Local technology stack">
        <div className="section-heading-row">
          <h2>Local tech stack and models</h2>
          <p className="hint">Every listed component has a local/on-premises operating path for the enterprise target.</p>
        </div>
        <div className="stack-grid">
          {STACK_ITEMS.map((item) => (
            <article key={item.label} className="stack-card">
              <span className="field-label">{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="architecture-section" aria-label="Secure data flow">
        <div className="section-heading-row">
          <h2>Secure local data flow</h2>
          <p className="hint">
            Access is intended only from corporate office Wi-Fi or an approved VPN into the on-premises network.
          </p>
        </div>
        <div className="network-flow-diagram">
          <section className="access-zone" aria-label="Access boundary">
            <span className="flow-zone-label">Access boundary</span>
            <div className="flow-node user-node">
              <span>Legal reviewer</span>
              <strong>Managed laptop</strong>
            </div>
            <div className="flow-condition">
              <span>Allowed path</span>
              <strong>Office Wi-Fi or VPN</strong>
            </div>
            <div className="flow-node blocked-node">
              <span>Blocked path</span>
              <strong>Public internet / unmanaged device</strong>
            </div>
          </section>

          <ol className="processing-flow" aria-label="Contract processing flow">
            <li>
              <span>01</span>
              <strong>Upload contract</strong>
              <p>Browser sends PDF/DOCX to the internal portal.</p>
            </li>
            <li>
              <span>02</span>
              <strong>Validate and parse locally</strong>
              <p>Backend checks file type/size and extracts text server-side.</p>
            </li>
            <li>
              <span>03</span>
              <strong>Extract clauses</strong>
              <p>Pipeline segments clauses and normalizes attributes.</p>
            </li>
            <li>
              <span>04</span>
              <strong>Apply playbook rules</strong>
              <p>Deterministic engine assigns rule IDs, severity, and recommended actions.</p>
            </li>
            <li>
              <span>05</span>
              <strong>Return structured result</strong>
              <p>Findings, evidence, draft language, and provenance return to the portal.</p>
            </li>
          </ol>

          <aside className="optional-guidance-branch" aria-label="Optional guidance branch">
            <span className="flow-zone-label">Optional branch</span>
            <strong>Qdrant guidance</strong>
            <p>
              If Qdrant is available, supplemental playbook guidance is attached after risk rules are final. If unavailable,
              the review still completes and risk output is unchanged.
            </p>
          </aside>
        </div>
      </section>

      <section className="architecture-section" aria-label="Trust boundaries">
        <h2>Trust boundaries</h2>
        <div className="trust-boundary-grid">
          <article>
            <h3>Document text</h3>
            <p>Uploaded content is processed server-side and is not exposed through dashboard history or config APIs.</p>
          </article>
          <article>
            <h3>Model calls</h3>
            <p>Model-assisted extraction uses the configured Ollama-compatible endpoint; fallback stays rules-only.</p>
          </article>
          <article>
            <h3>Guidance retrieval</h3>
            <p>Qdrant only supplies supplemental guidance. It cannot change rule IDs, severity, or missing-clause output.</p>
          </article>
          <article>
            <h3>Credentials</h3>
            <p>Runtime credentials are write-only, stored server-side, never pre-filled, and never returned to the browser.</p>
          </article>
        </div>
      </section>
    </div>
  );
}
