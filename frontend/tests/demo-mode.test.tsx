import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "../src/App";
import type { RuntimeConfig } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    getConfig: vi.fn(),
  };
});

import { getConfig } from "../src/api/client";

const BASE_CONFIG: RuntimeConfig = {
  deployment_mode: "local",
  provider_type: "ollama",
  model_name: "qwen3.6:35b",
  base_url_display: "configured, hidden",
  has_credential: false,
  playbook_id: "defense-services-v1",
  synthetic_data_only: false,
};

function renderApp() {
  render(
    <MemoryRouter initialEntries={["/review/new"]}>
      <App />
    </MemoryRouter>,
  );
}

describe("App demo-mode presentation (P7)", () => {
  it("shows the full nav and no demo warning in local mode", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);

    renderApp();

    await waitFor(() => expect(screen.getByText("New review")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /admin/i })).toBeInTheDocument();
    expect(screen.queryByRole("status", { name: /demo mode/i })).not.toBeInTheDocument();
  });

  it("shows the full nav without a demo warning banner in demo mode", async () => {
    vi.mocked(getConfig).mockResolvedValue({ ...BASE_CONFIG, deployment_mode: "demo", synthetic_data_only: true });

    renderApp();

    await waitFor(() => expect(screen.getByRole("link", { name: /^dashboard$/i })).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /^dashboard$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^new review$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^architecture$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^playbook$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^admin$/i })).toBeInTheDocument();
    expect(screen.queryByText(/demo mode/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/synthetic data only/i)).not.toBeInTheDocument();
  });
});
