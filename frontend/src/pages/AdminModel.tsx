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
    setBaseUrl(loaded.base_url_display);
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
      if (isOllama && baseUrl !== config?.base_url_display) update.base_url = baseUrl;
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
      <h1>Model &amp; provider configuration</h1>
      <p className="enterprise-note">Docker Ollama/local is the PoC verification path; local inference is the target enterprise mode.</p>
      <p className="demo-warning">Cloud-provider processing is for synthetic Demo data only.</p>

      {loadError && (
        <p className="form-error" role="alert">
          {loadError}
        </p>
      )}

      {config && (
        <form className="config-form" onSubmit={handleSave}>
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
                <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="http://ollama:11434" />
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

          {config.deployment_mode === "demo" && (
            <p className="hint">An admin-entered credential is an in-memory override and clears on service restart.</p>
          )}

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

          {testResult && (
            <p className={testResult.ok ? "test-result-ok" : "test-result-fail"} role="status">
              {testResult.ok
                ? `Connected to ${testResult.provider_type} (${testResult.model_name}) in ${testResult.latency_ms}ms`
                : `Connection failed for ${testResult.provider_type}`}
            </p>
          )}
          {testError && (
            <p className="test-result-fail" role="alert">
              {testError}
            </p>
          )}
        </form>
      )}
    </div>
  );
}
