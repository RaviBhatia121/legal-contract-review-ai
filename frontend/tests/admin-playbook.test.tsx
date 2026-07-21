import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { AdminPlaybook } from "../src/pages/AdminPlaybook";
import type { Playbook, RuntimeConfig } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    getActivePlaybook: vi.fn(),
    getConfig: vi.fn(),
    listReviews: vi.fn(),
  };
});

import { ApiRequestError, getActivePlaybook, getConfig, listReviews } from "../src/api/client";

const BASE_CONFIG: RuntimeConfig = {
  deployment_mode: "local",
  provider_type: "ollama",
  model_name: "qwen3.6:35b",
  base_url_display: "configured, hidden",
  has_credential: false,
  playbook_id: "defense-services-v1",
  synthetic_data_only: false,
};

const PLAYBOOK: Playbook = {
  playbook_id: "defense-services-v1",
  playbook_version: "1.0-draft",
  editable: false,
  edit_policy: "Read-only in this PoC. Playbook CRUD requires versioning, validation, audit trail, rollback, and explicit approval.",
  clause_types: ["confidentiality", "data_handling", "audit_inspection", "unknown"],
  required_clause_types: ["confidentiality", "data_handling", "audit_inspection"],
  missing_clause_rule_by_type: {
    confidentiality: "CONF-003",
    data_handling: "DATA-004",
    audit_inspection: "AUD-001",
  },
  clause_families: [
    { clause_type: "confidentiality", required: true, missing_clause_rule_id: "CONF-003", rule_count: 3 },
    { clause_type: "data_handling", required: true, missing_clause_rule_id: "DATA-004", rule_count: 4 },
    { clause_type: "audit_inspection", required: true, missing_clause_rule_id: "AUD-001", rule_count: 2 },
  ],
  rules: [
    {
      rule_id: "DATA-001",
      area: "Data handling",
      clause_type: "data_handling",
      trigger: "Sensitive data may be processed or stored in external/public cloud or outside approved systems",
      severity: "Critical",
      recommended_action: "Restrict processing to approved client-controlled environments",
      missing_clause_rule: false,
    },
    {
      rule_id: "AUD-001",
      area: "Audit",
      clause_type: "audit_inspection",
      trigger: "Customer has no audit or inspection right over relevant controls",
      severity: "High",
      recommended_action: "Add risk-based audit and evidence-access rights",
      missing_clause_rule: true,
    },
  ],
};

function renderPlaybook() {
  render(
    <MemoryRouter initialEntries={["/admin/playbook"]}>
      <Routes>
        <Route path="/admin/playbook" element={<AdminPlaybook />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("AdminPlaybook", () => {
  it("shows a loading state", () => {
    vi.mocked(getActivePlaybook).mockReturnValue(new Promise(() => {}));
    renderPlaybook();
    expect(screen.getByText(/loading playbook/i)).toBeInTheDocument();
  });

  it("shows the active read-only playbook with clause families and rules", async () => {
    vi.mocked(getActivePlaybook).mockResolvedValue(PLAYBOOK);
    renderPlaybook();

    await waitFor(() => expect(screen.getByText("defense-services-v1")).toBeInTheDocument());
    expect(screen.getByText("1.0-draft")).toBeInTheDocument();
    expect(screen.getByText(/^Read-only:$/i)).toBeInTheDocument();
    expect(screen.getByText(/CRUD requires versioning/i)).toBeInTheDocument();
    expect(screen.getByText("DATA-001")).toBeInTheDocument();
    expect(screen.getByText("AUD-001")).toBeInTheDocument();
    expect(screen.getByText(/^Missing clause$/i)).toBeInTheDocument();
    expect(screen.getAllByText(/audit inspection/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.queryByRole("button", { name: /save|delete|update|remove/i })).not.toBeInTheDocument();
  });

  it("shows API load errors", async () => {
    vi.mocked(getActivePlaybook).mockRejectedValue(
      new ApiRequestError({ code: "INTERNAL_ERROR", message: "Could not load playbook.", retryable: false }),
    );
    renderPlaybook();
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/could not load playbook/i));
  });
});

describe("Playbook nav visibility", () => {
  it("shows Playbook nav in local mode", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole("link", { name: /^playbook$/i })).toBeInTheDocument());
  });

  it("shows Playbook nav in hosted demo mode too", async () => {
    vi.mocked(getConfig).mockResolvedValue({ ...BASE_CONFIG, deployment_mode: "demo", synthetic_data_only: true });
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole("link", { name: /^dashboard$/i })).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /^playbook$/i })).toBeInTheDocument();
  });
});
