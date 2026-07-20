import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { ReviewNew } from "../src/pages/ReviewNew";
import { ReviewStatus } from "../src/pages/ReviewStatus";
import type { ReviewResult } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    createReview: vi.fn(),
    getReview: vi.fn(),
  };
});

import { createReview, getReview } from "../src/api/client";

const COMPLETED_RESULT: ReviewResult = {
  schema_version: "1.0-draft",
  review_id: "review-123",
  status: "completed",
  document: { name: "contract.pdf", sha256: "abc123", page_count: 10, language: "en" },
  review_summary: {
    overall_risk: "Critical",
    clauses_reviewed: 7,
    findings_total: 2,
    findings_by_risk: { Critical: 1, High: 1, Medium: 0, Low: 0 },
    missing_clause_count: 0,
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
      guidance: [
        {
          id: "G-DATA-001-1",
          text: "Sample negotiation guidance for DATA-001.",
          category: "negotiation_tip",
          source_note: "Illustrative negotiation guidance.",
          score: 0.9,
        },
      ],
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
    },
  ],
  missing_clauses: [],
  provenance: {
    deployment_mode: "local",
    department: "Legal",
    pipeline_version: "1.0-draft",
    playbook_version: "1.0-draft",
    prompt_version: "1.0-draft",
    parser_name: "none",
    parser_version: "p0-fixed-result",
    model_provider: "fixed-fixture",
    model_name: "none",
    model_revision: null,
    retrieval_mode: "degraded_full_rules",
    completed_at: "2026-07-18T10:00:00Z",
  },
};

describe("golden path: upload to findings", () => {
  it("submits an upload and renders the completed findings screen", async () => {
    const user = userEvent.setup();
    vi.mocked(createReview).mockResolvedValue({
      review_id: "review-123",
      status: "queued",
      status_url: "/api/v1/reviews/review-123",
    });
    vi.mocked(getReview).mockResolvedValue(COMPLETED_RESULT);

    render(
      <MemoryRouter initialEntries={["/review/new"]}>
        <Routes>
          <Route path="/review/new" element={<ReviewNew />} />
          <Route path="/reviews/:reviewId" element={<ReviewStatus />} />
        </Routes>
      </MemoryRouter>,
    );

    const file = new File(["%PDF-1.4 test content"], "contract.pdf", { type: "application/pdf" });
    const fileInput = screen.getByLabelText(/drag and drop/i) as HTMLInputElement;
    await user.upload(fileInput, file);

    const submitButton = screen.getByRole("button", { name: /review contract/i });
    await user.click(submitButton);

    expect(createReview).toHaveBeenCalledWith(file, "defense-services-v1");

    await waitFor(() => expect(screen.getByText("contract.pdf")).toBeInTheDocument());

    expect(screen.getByText(/overall risk: critical/i)).toBeInTheDocument();
    expect(screen.getByText("DATA-001")).toBeInTheDocument();
    expect(screen.getByText("CONF-002")).toBeInTheDocument();

    // P4: guidance is supplemental UI only — the label never shows the raw
    // "degraded_full_rules" enum value, and a finding with guidance items
    // renders its collapsible panel with the required disclaimer.
    expect(screen.getByText(/guidance unavailable, rule review unaffected/i)).toBeInTheDocument();
    expect(screen.queryByText("degraded_full_rules")).not.toBeInTheDocument();
    expect(screen.getByText(/supplemental guidance \(1\)/i)).toBeInTheDocument();
    expect(screen.getByText(/sample negotiation guidance for data-001/i)).toBeInTheDocument();
    expect(screen.getByText(/illustrative decision-support content, not legal advice/i)).toBeInTheDocument();
  });

  it("shows a validation error for an unsupported file type without calling the API", async () => {
    vi.mocked(createReview).mockClear();

    render(
      <MemoryRouter initialEntries={["/review/new"]}>
        <Routes>
          <Route path="/review/new" element={<ReviewNew />} />
        </Routes>
      </MemoryRouter>,
    );

    const file = new File(["hello"], "notes.txt", { type: "text/plain" });
    const fileInput = screen.getByLabelText(/drag and drop/i) as HTMLInputElement;
    // userEvent.upload enforces the input's `accept` attribute; use fireEvent
    // to exercise the component's own extension validation directly.
    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText(/upload a pdf or docx file/i)).toBeInTheDocument();
    expect(createReview).not.toHaveBeenCalled();
  });
});
