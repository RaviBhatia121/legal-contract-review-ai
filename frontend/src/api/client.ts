import type {
  ApiError,
  ConfigTestResult,
  ConfigUpdateRequest,
  ProviderInfo,
  ReviewCreated,
  ReviewResult,
  RuntimeConfig,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiRequestError extends Error {
  error: ApiError;

  constructor(error: ApiError) {
    super(error.message);
    this.error = error;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let error: ApiError = {
      code: "INTERNAL_ERROR",
      message: `Request failed with status ${response.status}`,
      retryable: false,
    };
    try {
      const body = await response.json();
      if (body?.error) {
        error = body.error;
      }
    } catch {
      // response body was not JSON; keep the generic error above
    }
    throw new ApiRequestError(error);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function createReview(file: File, playbookId: string): Promise<ReviewCreated> {
  const form = new FormData();
  form.append("file", file);
  form.append("playbook_id", playbookId);
  const response = await fetch(`${API_BASE}/reviews`, { method: "POST", body: form });
  return handleResponse<ReviewCreated>(response);
}

export async function getReview(reviewId: string): Promise<ReviewResult> {
  const response = await fetch(`${API_BASE}/reviews/${reviewId}`);
  return handleResponse<ReviewResult>(response);
}

export async function getConfig(): Promise<RuntimeConfig> {
  const response = await fetch(`${API_BASE}/config`);
  return handleResponse<RuntimeConfig>(response);
}

export async function getProviders(): Promise<ProviderInfo[]> {
  const response = await fetch(`${API_BASE}/config/providers`);
  return handleResponse<ProviderInfo[]>(response);
}

export async function updateConfig(update: ConfigUpdateRequest): Promise<RuntimeConfig> {
  const response = await fetch(`${API_BASE}/config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update),
  });
  return handleResponse<RuntimeConfig>(response);
}

export async function testConfig(): Promise<ConfigTestResult> {
  const response = await fetch(`${API_BASE}/config/test`, { method: "POST" });
  return handleResponse<ConfigTestResult>(response);
}
