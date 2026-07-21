import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AdminModel } from "../src/pages/AdminModel";
import type { ConfigTestResult, ProviderInfo, RuntimeConfig } from "../src/api/types";

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    getConfig: vi.fn(),
    getProviders: vi.fn(),
    updateConfig: vi.fn(),
    testConfig: vi.fn(),
  };
});

import { ApiRequestError, getConfig, getProviders, testConfig, updateConfig } from "../src/api/client";

const BASE_CONFIG: RuntimeConfig = {
  deployment_mode: "local",
  provider_type: "ollama",
  model_name: "qwen3.6:35b",
  base_url_display: "http://***.***.***.***:11434",
  has_credential: false,
  playbook_id: "defense-services-v1",
  synthetic_data_only: false,
};

const PROVIDERS: ProviderInfo[] = [
  { provider_type: "ollama", implemented: true },
  { provider_type: "anthropic", implemented: false },
  { provider_type: "openai", implemented: false },
  { provider_type: "gemini", implemented: false },
];

function renderAdmin() {
  render(
    <MemoryRouter initialEntries={["/admin/model"]}>
      <Routes>
        <Route path="/admin/model" element={<AdminModel />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("AdminModel", () => {
  it("renders the current config and never pre-fills the credential field", async () => {
    vi.mocked(getConfig).mockResolvedValue({ ...BASE_CONFIG, has_credential: true });
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);

    renderAdmin();

    await waitFor(() => expect(screen.getByDisplayValue("qwen3.6:35b")).toBeInTheDocument());
    expect(screen.getByPlaceholderText(/hidden; enter a new url to replace/i)).toBeInTheDocument();
    expect(screen.queryByDisplayValue(/192\.168\.0\.72/)).not.toBeInTheDocument();

    const credentialInput = screen.getByPlaceholderText("Credential configured") as HTMLInputElement;
    expect(credentialInput.value).toBe("");
    expect(screen.getByText(/configured, never displayed/i)).toBeInTheDocument();
  });

  it("explains runtime configuration without overclaiming disabled providers", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);

    renderAdmin();

    await waitFor(() => expect(screen.getByRole("heading", { name: /runtime provider configuration/i })).toBeInTheDocument());

    expect(screen.getByText(/not a chatbot setting/i)).toBeInTheDocument();
    expect(screen.getByText(/final risk labels come from the rule engine/i)).toBeInTheDocument();
    expect(screen.getByText(/ollama is the enabled provider/i)).toBeInTheDocument();
    expect(screen.getByText(/gemini remain disabled catalog placeholders/i)).toBeInTheDocument();
    expect(screen.getByText(/disabled placeholders: anthropic, openai, gemini/i)).toBeInTheDocument();
  });

  it("disables not-enabled providers in the select", async () => {
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);

    renderAdmin();

    await waitFor(() => expect(screen.getByRole("combobox")).toBeInTheDocument());
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    const anthropicOption = within(select).getByText(/anthropic/i) as HTMLOptionElement;
    expect(anthropicOption.disabled).toBe(true);
    const ollamaOption = within(select).getByText(/^ollama$/i) as HTMLOptionElement;
    expect(ollamaOption.disabled).toBe(false);
    expect(screen.getAllByText(/not enabled/i).length).toBeGreaterThanOrEqual(3);
  });

  it("saves an updated model name and shows confirmation", async () => {
    const user = userEvent.setup();
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);
    vi.mocked(updateConfig).mockResolvedValue({ ...BASE_CONFIG, model_name: "qwen3:8b" });

    renderAdmin();

    await waitFor(() => expect(screen.getByDisplayValue("qwen3.6:35b")).toBeInTheDocument());
    const modelInput = screen.getByDisplayValue("qwen3.6:35b");
    await user.clear(modelInput);
    await user.type(modelInput, "qwen3:8b");
    await user.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(updateConfig).toHaveBeenCalledWith(expect.objectContaining({ model_name: "qwen3:8b" })));
    expect(updateConfig).toHaveBeenCalledWith(expect.not.objectContaining({ base_url: expect.any(String) }));
    expect(screen.getByText(/configuration saved/i)).toBeInTheDocument();
  });

  it("shows the rejection message when saving an unimplemented provider fails server-side", async () => {
    const user = userEvent.setup();
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);
    vi.mocked(updateConfig).mockRejectedValue(
      new ApiRequestError({
        code: "CONFIGURATION_INVALID",
        message: "provider_type 'anthropic' is not yet implemented and cannot be saved as active configuration.",
        retryable: false,
      }),
    );

    renderAdmin();

    await waitFor(() => expect(screen.getByDisplayValue("qwen3.6:35b")).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/not yet implemented/i));
  });

  it("shows a successful test-connection result", async () => {
    const user = userEvent.setup();
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);
    const result: ConfigTestResult = { ok: true, provider_type: "ollama", model_name: "qwen3.6:35b", latency_ms: 42 };
    vi.mocked(testConfig).mockResolvedValue(result);

    renderAdmin();

    await waitFor(() => expect(screen.getByRole("button", { name: /test connection/i })).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: /test connection/i }));

    await waitFor(() => expect(screen.getByText(/connected to ollama/i)).toBeInTheDocument());
    expect(screen.getByText(/42ms/i)).toBeInTheDocument();
    expect(screen.getByText(/reachability check only/i)).toBeInTheDocument();
  });

  it("does not show a demo-mode lock warning in the polished hosted admin screen", async () => {
    vi.mocked(getConfig).mockResolvedValue({ ...BASE_CONFIG, deployment_mode: "demo", synthetic_data_only: true });
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);

    renderAdmin();

    await waitFor(() => expect(screen.getByDisplayValue("demo")).toBeInTheDocument());
    expect(screen.queryByText(/demo mode locks production configuration changes server-side/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/clears on service restart/i)).not.toBeInTheDocument();
  });

  it("shows a failed test-connection result without exposing provider internals", async () => {
    const user = userEvent.setup();
    vi.mocked(getConfig).mockResolvedValue(BASE_CONFIG);
    vi.mocked(getProviders).mockResolvedValue(PROVIDERS);
    vi.mocked(testConfig).mockRejectedValue(
      new ApiRequestError({ code: "PROVIDER_UNAVAILABLE", message: "The configured model provider is unavailable.", retryable: true }),
    );

    renderAdmin();

    await waitFor(() => expect(screen.getByRole("button", { name: /test connection/i })).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: /test connection/i }));

    await waitFor(() => expect(screen.getByText(/unavailable/i)).toBeInTheDocument());
  });
});
