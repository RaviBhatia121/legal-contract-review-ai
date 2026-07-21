import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { Architecture } from "../src/pages/Architecture";
import type { RuntimeConfig } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    getConfig: vi.fn(),
    listReviews: vi.fn(),
  };
});

import { getConfig, listReviews } from "../src/api/client";

const BASE_CONFIG: RuntimeConfig = {
  deployment_mode: "local",
  provider_type: "ollama",
  model_name: "qwen3.6:35b",
  base_url_display: "http://***.***.***.***:11434",
  has_credential: false,
  playbook_id: "defense-services-v1",
  synthetic_data_only: false,
};

function renderArchitecture() {
  vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
  render(
    <MemoryRouter initialEntries={["/architecture"]}>
      <Routes>
        <Route path="/architecture" element={<Architecture />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("Architecture", () => {
  it("shows the configured model path and local stack", async () => {
    renderArchitecture();

    await waitFor(() => expect(screen.getByText("qwen3.6:35b")).toBeInTheDocument());
    expect(screen.getByText("http://***.***.***.***:11434")).toBeInTheDocument();
    expect(screen.queryByText(/192\.168\.0\.72/)).not.toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
    expect(screen.getByText("Haystack 2.x pipeline")).toBeInTheDocument();
    expect(screen.getByText("Qdrant")).toBeInTheDocument();
    expect(screen.getByText("React + Vite")).toBeInTheDocument();
    expect(screen.getByText(/no public AI API required/i)).toBeInTheDocument();
  });

  it("shows the secure data-flow walkthrough and trust boundaries", async () => {
    renderArchitecture();

    await waitFor(() => expect(screen.getByText("Upload contract")).toBeInTheDocument());
    expect(screen.getByText(/Office Wi-Fi or VPN/i)).toBeInTheDocument();
    expect(screen.getByText(/Public internet \/ unmanaged device/i)).toBeInTheDocument();
    expect(screen.getByText("Validate and parse locally")).toBeInTheDocument();
    expect(screen.getByText("Apply playbook rules")).toBeInTheDocument();
    expect(screen.getByText(/Qdrant guidance/i)).toBeInTheDocument();
    expect(screen.getByText(/If Qdrant is available/i)).toBeInTheDocument();
    expect(screen.getByText(/Qdrant only supplies supplemental guidance/i)).toBeInTheDocument();
    expect(screen.getByText(/Credentials are write-only/i)).toBeInTheDocument();
  });
});

describe("Architecture nav", () => {
  it("shows Architecture nav in local and demo modes", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(listReviews).mockResolvedValue({ items: [], limit: 50, offset: 0 });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByRole("link", { name: /^architecture$/i })).toBeInTheDocument());
  });
});
