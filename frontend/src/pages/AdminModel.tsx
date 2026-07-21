import { useEffect, useState } from "react";
import { ApiRequestError, getConfig, getProviders, testConfig, updateConfig } from "../api/client";
import type { ConfigTestResult, ProviderInfo, RuntimeConfig } from "../api/types";

export function AdminModel() {
  const [config, setConfig] = useState<RuntimeConfig | null>(null);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [providerType, setProviderType] = useState("");
  const [modelName, setModelName] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [baseUrlDirty, setBaseUrlDirty] = useState(false);
  const [credential, setCredential] = useState("");

  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [testResult, setTestResult] = useState<ConfigTestResult | null>(null);
  const [testError, setTestError] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);

  function applyConfig(loaded: RuntimeConfig) {
    setConfig(loaded);
    setProviderType(loaded.provider_type);
    setModelName(loaded.model_name);
    setBaseUrl("");
    setBaseUrlDirty(false);
  }

  useEffect(() => {
    Promise.all([getConfig(), getProviders()])
      .then(([loadedConfig, loadedProviders]) => {
        applyConfig(loadedConfig);
        setProviders(loadedProviders);
      })
      .catch(() => setLoadError("Could not load runtime configuration."));
  }, []);

  const isOllama = providerType === "ollama";
  const enabledProviders = providers.filter((provider) => provider.implemented);
  const disabledProviders = providers.filter((provider) => !provider.implemented);

  async function handleSave(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    setTestResult(null);
    setTestError(null);
    try {
      const update: Record<string, string> = {};
      if (providerType !== config?.provider_type) update.provider_type = providerType;
      if (modelName !== config?.model_name) update.model_name = modelName;
      if (isOllama && baseUrlDirty) update.base_url = baseUrl.trim();
      if (credential) update.credential = credential;

      const updated = await updateConfig(update);
      applyConfig(updated);
      setCredential("");
      setSaved(true);
    } catch (err) {
      setSaveError(err instanceof ApiRequestError ? err.error.message : "Could not save configuration.");
    } finally {
      setSaving(false);
    }
  }

  async function handleTest() {
    setTesting(true);
    setTestError(null);
    setTestResult(null);
    try {
      const result = await testConfig();
      setTestResult(result);
    } catch (err) {
      setTestError(err instanceof ApiRequestError ? err.error.message : "Connection test failed.");
    } finally {
      setTesting(false);
    }
  }

  return (
    <div className="page admin-model">
      <h1>Runtime Provider Configuration</h1>
      <p className="lede">
        Configure the model runtime used by the structured review pipeline. This is provider
        orchestration for clause classification and extraction, not a chatbot setting.
      </p>

      <div className="admin-hero-grid" aria-label="Configuration posture">
        <section className="admin-info-card">
          <h2>Default review mode</h2>
          <p>
            Deterministic playbook evaluation remains the risk-scoring authority. Model
            output can assist extraction, but final risk labels come from the rule engine.
          </p>
        </section>
        <section className="admin-info-card">
          <h2>Local runtime path</h2>
          <p>
            Docker Ollama is the verified local model runtime path for this PoC and the
            production-target architecture remains private infrastructure.
          </p>
        </section>
        <section className="admin-info-card">
          <h2>Hosted providers</h2>
          <p>
            Ollama is the enabled provider for hosted and local model-assisted review.
            Anthropic, OpenAI, and Gemini remain disabled catalog placeholders.
          </p>
        </section>
      </div>

      {loadError && (
        <p className="form-error" role="alert">
          {loadError}
        </p>
      )}

      {config && (
        <>
          <section className="current-config-card" aria-label="Current runtime configuration">
            <div>
              <span className="field-label">Active provider</span>
              <strong>{config.provider_type}</strong>
            </div>
            <div>
              <span className="field-label">Model</span>
              <strong>{config.model_name}</strong>
            </div>
            <div>
              <span className="field-label">Credential</span>
              <strong>{config.has_credential ? "Configured, never displayed" : "Not configured"}</strong>
            </div>
            <div>
              <span className="field-label">Deployment mode</span>
              <strong>{config.deployment_mode}</strong>
            </div>
          </section>

          <section className="provider-catalog" aria-label="Provider catalog">
            <div className="section-heading-row">
              <h2>Provider catalog</h2>
              <p className="hint">Only enabled providers can be saved as active configuration.</p>
            </div>
            <div className="provider-card-grid">
              {providers.map((provider) => (
                <article
                  key={provider.provider_type}
                  className={`provider-card ${provider.implemented ? "provider-enabled" : "provider-disabled"}`}
                >
                  <span className="provider-name">{provider.provider_type}</span>
                  <span className="provider-status">{provider.implemented ? "Enabled" : "Not enabled"}</span>
                </article>
              ))}
            </div>
            <p className="hint">
              Enabled now: {enabledProviders.map((provider) => provider.provider_type).join(", ") || "none"}.
              Disabled placeholders: {disabledProviders.map((provider) => provider.provider_type).join(", ") || "none"}.
            </p>
          </section>

          <form className="config-form" onSubmit={handleSave}>
          <div className="section-heading-row">
            <h2>Runtime settings</h2>
            <p className="hint">Credentials are write-only. Saved secret values are never returned to the browser.</p>
          </div>
          <div className="config-fields">
            <label>
              Deployment mode
              <input value={config.deployment_mode} disabled readOnly />
            </label>

            <label>
              Provider
              <select value={providerType} onChange={(e) => setProviderType(e.target.value)}>
                {providers.map((p) => (
                  <option key={p.provider_type} value={p.provider_type} disabled={!p.implemented}>
                    {p.provider_type}
                    {!p.implemented ? " (Not enabled)" : ""}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Model name
              <input value={modelName} onChange={(e) => setModelName(e.target.value)} />
            </label>

            {isOllama && (
              <label>
                Base URL
                <input
                  value={baseUrl}
                  onChange={(e) => {
                    setBaseUrl(e.target.value);
                    setBaseUrlDirty(true);
                  }}
                  placeholder={`${config.base_url_display} (hidden; enter a new URL to replace)`}
                />
              </label>
            )}

            <label>
              Credential
              <input
                type="password"
                value={credential}
                onChange={(e) => setCredential(e.target.value)}
                placeholder={config.has_credential ? "Credential configured" : "Not configured"}
                autoComplete="new-password"
              />
            </label>

            <label>
              Playbook
              <input value={config.playbook_id} disabled readOnly />
            </label>
          </div>

          <div className="security-notes" aria-label="Configuration security notes">
            <h2>Security notes</h2>
            <ul>
              <li>Credentials are write-only and never displayed after save.</li>
              <li>Connection test checks reachability of the configured provider only.</li>
              <li>Disabled providers are visible for portability planning, not active processing.</li>
            </ul>
          </div>

          {saveError && (
            <p className="form-error" role="alert">
              {saveError}
            </p>
          )}
          {saved && !saveError && <p className="hint">Configuration saved.</p>}

          <div className="config-actions">
            <button type="submit" className="primary-action" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
            <button type="button" onClick={handleTest} disabled={testing}>
              {testing ? "Testing…" : "Test connection"}
            </button>
          </div>

          <div className="connection-test-panel" aria-label="Connection test result">
            <h2>Connection test</h2>
            <p className="hint">Reachability check only; it does not run a contract review or expose credentials.</p>
            {testResult && (
              <p className={testResult.ok ? "test-result-ok" : "test-result-fail"} role="status">
                {testResult.ok
                  ? `Connected to ${testResult.provider_type} (${testResult.model_name}) in ${testResult.latency_ms}ms`
                  : `Connection failed for ${testResult.provider_type}`}
              </p>
            )}
            {testError && (
              <p className="test-result-fail" role="alert">
                {testError} Model-assisted review is unavailable. Reviews will use deterministic fallback until
                Ollama/model is available.
              </p>
            )}
          </div>
          </form>
        </>
      )}
    </div>
  );
}
