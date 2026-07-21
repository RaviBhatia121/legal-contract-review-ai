import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { Dashboard } from "../src/pages/Dashboard";
import type { ReviewListOut, ReviewSummaryItem, RuntimeConfig } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    listReviews: vi.fn(),
    getConfig: vi.fn(),
  };
});

import { ApiRequestError, getConfig, listReviews } from "../src/api/client";

const BASE_CONFIG: RuntimeConfig = {
  deployment_mode: "local",
  provider_type: "ollama",
  model_name: "qwen3.6:35b",
  base_url_display: "configured, hidden",
  has_credential: false,
  playbook_id: "defense-services-v1",
  synthetic_data_only: false,
};

function item(overrides: Partial<ReviewSummaryItem>): ReviewSummaryItem {
  return {
    review_id: "review-1",
    document_name: "contract.pdf",
    status: "completed",
    overall_risk: "Critical",
    created_at: "2026-07-20T10:00:00Z",
    completed_at: "2026-07-20T10:00:05Z",
    findings_total: 8,
    missing_clause_count: 1,
    needs_review_count: 0,
    deployment_mode: "local",
    retrieval_mode: "degraded_full_rules",
    ...overrides,
  };
}

function renderDashboard() {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("Dashboard", () => {
  it("shows a loading state before data arrives", () => {
    vi.mocked(listReviews).mockReturnValue(new Promise(() => {}));
    renderDashboard();
    expect(screen.getByText(/loading dashboard/i)).toBeInTheDocument();
  });

  it("shows the API error message on failure", async () => {
    vi.mocked(listReviews).mockRejectedValue(
      new ApiRequestError({ code: "INTERNAL_ERROR", message: "Could not reach the server.", retryable: false }),
    );
    renderDashboard();
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/could not reach the server/i));
  });

  it("shows an empty state with no reviews", async () => {
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 } satisfies ReviewListOut);
    renderDashboard();
    await waitFor(() => expect(screen.getByText(/no reviews yet/i)).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /new review/i })).toBeInTheDocument();
  });

  it("computes real stats and renders the recent-reviews table, never labelling counts as totals", async () => {
    const items: ReviewSummaryItem[] = [
      item({ review_id: "r1", document_name: "critical.pdf", overall_risk: "Critical", status: "completed" }),
      item({ review_id: "r2", document_name: "low-risk.pdf", overall_risk: "Low", status: "completed", retrieval_mode: "qdrant" }),
      item({ review_id: "r3", document_name: "in-flight.pdf", overall_risk: null, completed_at: null, status: "parsing" }),
      item({ review_id: "r4", document_name: "broken.pdf", overall_risk: null, completed_at: null, status: "failed" }),
    ];
    vi.mocked(listReviews).mockResolvedValue({ items, limit: 50, offset: 0 } satisfies ReviewListOut);
    renderDashboard();

    await waitFor(() => expect(screen.getByText("critical.pdf")).toBeInTheDocument());

    // Reviews shown is explicitly scoped — never "Total reviews"/"All reviews".
    expect(screen.getByText(/reviews shown/i)).toBeInTheDocument();
    expect(screen.queryByText(/total reviews/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/all reviews/i)).not.toBeInTheDocument();
    expect(screen.getByText(/up to 50 most recently retained/i)).toBeInTheDocument();

    // No fake ROI/value framing anywhere on the page.
    expect(screen.queryByText(/hours saved/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/money saved/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/risk(s)? prevented/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/roi/i)).not.toBeInTheDocument();

    // Counts computed from the fixed mock set.
    const stats = screen.getByLabelText(/review history summary/i);
    expect(stats).toHaveTextContent("4 (up to 50 most recently retained)");
    expect(screen.getByText("critical.pdf")).toBeInTheDocument();
    expect(screen.getByText("low-risk.pdf")).toBeInTheDocument();
    expect(screen.getByText("in-flight.pdf")).toBeInTheDocument();
    expect(screen.getByText("broken.pdf")).toBeInTheDocument();
    expect(screen.getByLabelText(/review operating modes/i)).toHaveTextContent(/1 with supplemental guidance/i);
    expect(screen.getByLabelText(/review operating modes/i)).toHaveTextContent(/1 completed without guidance/i);
    expect(screen.queryByText(/degraded_full_rules/i)).not.toBeInTheDocument();

    const viewLink = screen.getByRole("link", { name: /view review for critical\.pdf/i });
    expect(viewLink).toHaveAttribute("href", "/reviews/r1");
  });
});

describe("Dashboard nav visibility (P8.3)", () => {
  it("shows the Dashboard nav link in local mode", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 } satisfies ReviewListOut);
    render(
      <MemoryRouter initialEntries={["/review/new"]}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole("link", { name: /^dashboard$/i })).toBeInTheDocument());
  });

  it("shows the Dashboard nav link in demo mode too (unlike Admin)", async () => {
    vi.mocked(getConfig).mockResolvedValue({ ...BASE_CONFIG, deployment_mode: "demo", synthetic_data_only: true });
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 } satisfies ReviewListOut);
    render(
      <MemoryRouter initialEntries={["/review/new"]}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole("link", { name: /^dashboard$/i })).toBeInTheDocument());
    expect(screen.queryByRole("link", { name: /admin/i })).not.toBeInTheDocument();
  });

  it("renders Dashboard content at the root route instead of redirecting", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 } satisfies ReviewListOut);
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole("heading", { name: /defense services review console/i })).toBeInTheDocument());
    expect(screen.queryByText(/start a contract review/i)).not.toBeInTheDocument();
  });
});
