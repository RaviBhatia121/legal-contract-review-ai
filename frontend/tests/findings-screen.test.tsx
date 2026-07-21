import { render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { ReviewStatus } from "../src/pages/ReviewStatus";
import type { ReviewResult } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    getReview: vi.fn(),
  };
});

import { getReview } from "../src/api/client";

const RESULT: ReviewResult = {
  schema_version: "1.0-draft",
  review_id: "review-999",
  status: "completed",
  document: { name: "sentinel-support-agreement.pdf", sha256: "def456", page_count: 12, language: "en" },
  review_summary: {
    overall_risk: "Critical",
    clauses_reviewed: 9,
    findings_total: 3,
    findings_by_risk: { Critical: 1, High: 1, Medium: 0, Low: 0 },
    missing_clause_count: 1,
    needs_review_count: 0,
  },
  findings: [
    {
      finding_id: "f-1",
      finding_type: "deviation",
      clause_id: "c-1",
      clause_type: "data_handling",
      title: "Data Hosting",
      section_reference: "Section 6.2",
      page_start: 4,
      page_end: 4,
      evidence_text: "The Supplier may process Customer Data using regional public cloud services.",
      classification_confidence: 0.96,
      risk_label: "Critical",
      rule_id: "DATA-001",
      deviation_reason: "Processing outside approved systems.",
      recommended_action: "Restrict processing to approved environments.",
      needs_review: false,
      source: "rule",
      guidance: [],
      suggested_draft_clause: {
        text: "Supplier shall process and store Customer Data only within Buyer-approved, client-controlled environments.",
        source: "approved_template",
        approval_note: "Drafting support only; legal approval required before use.",
      },
    },
    {
      finding_id: "f-2",
      finding_type: "deviation",
      clause_id: "c-2",
      clause_type: "confidentiality",
      title: "Confidentiality",
      section_reference: "Section 9.3",
      page_start: 6,
      page_end: 6,
      evidence_text: "Affiliate disclosure clause text.",
      classification_confidence: 0.93,
      risk_label: "High",
      rule_id: "CONF-002",
      deviation_reason: "No need-to-know restriction.",
      recommended_action: "Require need-to-know access.",
      needs_review: false,
      source: "rule",
      guidance: [],
      suggested_draft_clause: null,
    },
  ],
  missing_clauses: [
    {
      finding_id: "f-3",
      finding_type: "missing_clause",
      clause_id: null,
      clause_type: "audit_inspection",
      title: "Audit / Inspection right missing",
      section_reference: null,
      page_start: null,
      page_end: null,
      evidence_text: null,
      classification_confidence: null,
      risk_label: "High",
      rule_id: "AUD-001",
      deviation_reason: "Required clause not found in the document.",
      recommended_action: "Add an audit and inspection clause.",
      needs_review: false,
      source: "rule",
      guidance: [],
      suggested_draft_clause: {
        text: "Buyer may conduct reasonable risk-based audits and evidence reviews.",
        source: "approved_template",
        approval_note: "Drafting support only; legal approval required before use.",
      },
    },
  ],
  provenance: {
    deployment_mode: "local",
    department: "Legal",
    pipeline_version: "1.0-draft",
    playbook_version: "1.0-draft",
    prompt_version: "1.0-draft",
    parser_name: "pypdf",
    parser_version: "1.0",
    model_provider: "none",
    model_name: "none",
    model_revision: null,
    retrieval_mode: "degraded_full_rules",
    completed_at: "2026-07-20T10:00:00Z",
  },
};

function renderFindingsScreen() {
  render(
    <MemoryRouter initialEntries={["/reviews/review-999"]}>
      <Routes>
        <Route path="/reviews/:reviewId" element={<ReviewStatus />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("findings screen (P8.5 polish)", () => {
  it("shows the compliance banner with its three required claims", async () => {
    vi.mocked(getReview).mockResolvedValue(RESULT);
    renderFindingsScreen();

    await waitFor(() => expect(screen.getByText("sentinel-support-agreement.pdf")).toBeInTheDocument());

    expect(screen.getByText(/findings are decision support only, not legal advice/i)).toBeInTheDocument();
    expect(screen.getByText(/final risk labels are assigned by the deterministic playbook rule engine/i)).toBeInTheDocument();
    expect(
      screen.getByText(/supplemental guidance, when shown, is illustrative context only and does not change any finding's risk label/i),
    ).toBeInTheDocument();
  });

  it("groups deviation findings under severity headings and keeps missing clauses in their own section", async () => {
    vi.mocked(getReview).mockResolvedValue(RESULT);
    renderFindingsScreen();

    await waitFor(() => expect(screen.getByText("sentinel-support-agreement.pdf")).toBeInTheDocument());

    const criticalGroup = screen.getByLabelText(/critical severity findings/i);
    expect(within(criticalGroup).getByText("DATA-001")).toBeInTheDocument();

    const highGroup = screen.getByLabelText(/high severity findings/i);
    expect(within(highGroup).getByText("CONF-002")).toBeInTheDocument();
    expect(within(highGroup).queryByText("AUD-001")).not.toBeInTheDocument();

    const missingSection = screen.getByLabelText(/missing clauses/i);
    expect(within(missingSection).getByText("AUD-001")).toBeInTheDocument();
  });

  it("labels the evidence, reasoning, and recommendation fields without losing content", async () => {
    vi.mocked(getReview).mockResolvedValue(RESULT);
    renderFindingsScreen();

    await waitFor(() => expect(screen.getByText("sentinel-support-agreement.pdf")).toBeInTheDocument());

    expect(screen.getAllByText("Evidence").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Why this is flagged").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Recommended action").length).toBeGreaterThan(0);
    expect(
      screen.getByText("The Supplier may process Customer Data using regional public cloud services."),
    ).toBeInTheDocument();
    expect(screen.getByText("Restrict processing to approved environments.")).toBeInTheDocument();
  });

  it("shows a page heading and does not lose the severity/missing-clause counts", async () => {
    vi.mocked(getReview).mockResolvedValue(RESULT);
    renderFindingsScreen();

    await waitFor(() => expect(screen.getByText("sentinel-support-agreement.pdf")).toBeInTheDocument());

    expect(screen.getByRole("heading", { level: 1, name: /review result/i })).toBeInTheDocument();
    expect(screen.getByText(/missing clauses: 1/i)).toBeInTheDocument();
    expect(screen.getByText(/needs review: 0/i)).toBeInTheDocument();
  });

  it("shows approved-template drafting support when available", async () => {
    vi.mocked(getReview).mockResolvedValue(RESULT);
    renderFindingsScreen();

    await waitFor(() => expect(screen.getByText("sentinel-support-agreement.pdf")).toBeInTheDocument());

    expect(screen.getAllByText(/suggested approved clause language/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/client-controlled environments/i)).toBeInTheDocument();
    expect(screen.getAllByText(/legal approval required/i).length).toBeGreaterThan(0);
  });

  it("explains degraded Qdrant guidance without exposing the raw enum", async () => {
    vi.mocked(getReview).mockResolvedValue(RESULT);
    renderFindingsScreen();

    await waitFor(() => expect(screen.getByText("sentinel-support-agreement.pdf")).toBeInTheDocument());

    const guidanceStatus = screen.getByLabelText(/supplemental guidance status/i);
    expect(guidanceStatus).toHaveTextContent(/Qdrant guidance unavailable/i);
    expect(guidanceStatus).toHaveTextContent(/review completed with deterministic playbook rules only/i);
    expect(screen.queryByText(/degraded_full_rules/i)).not.toBeInTheDocument();
  });
});
