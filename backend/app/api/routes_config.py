from fastapi import APIRouter

from app.api import errors
from app.core.config import get_settings
from app.model_adapter.errors import ModelAdapterError
from app.model_adapter.ollama_adapter import OllamaAdapter
from app.schemas.review import ConfigOut, ConfigTestResult, ConfigUpdate, ProviderInfo
from app.services.ssrf_guard import SsrfValidationError, validate_ollama_base_url

router = APIRouter(prefix="/api/v1/config", tags=["config"])

# In-memory admin override, cleared on process restart (matches API_CONTRACT.md
# hosted-demo credential-override behavior). P0 does not call any real provider.
_runtime_override = {
    "provider_type": None,
    "model_name": None,
    "base_url_display": None,
    "has_credential": False,
}

# Full catalog shown in the admin UI (UI_SPEC.md "Provider catalog"). Not the
# same as what can actually be saved — see _SAVEABLE_PROVIDERS below.
_ALLOWED_PROVIDERS = {"ollama", "anthropic", "openai", "gemini"}

# P5 correction: only `ollama` can be set as the *active* configuration.
# Anthropic/OpenAI/Gemini remain visible in the catalog (disabled, "Not
# enabled") to demonstrate provider portability via the same ModelAdapter
# interface, but D-05 (hosted demo provider) is still Open — PUT /config
# rejects any attempt to select them rather than silently accepting or
# ignoring the request. Implementing a real cloud adapter is out of scope
# for P5 and requires a separate explicit decision.
_SAVEABLE_PROVIDERS = {"ollama"}


@router.get("", response_model=ConfigOut)
async def get_config() -> ConfigOut:
    settings = get_settings()
    return ConfigOut(
        deployment_mode=settings.deployment_mode,  # type: ignore[arg-type]
        provider_type=_runtime_override["provider_type"] or settings.provider_type,
        model_name=_runtime_override["model_name"] or settings.model_name,
        base_url_display=_runtime_override["base_url_display"] or settings.base_url_display,
        has_credential=_runtime_override["has_credential"],
        playbook_id=settings.playbook_id,
        synthetic_data_only=settings.deployment_mode == "demo",
    )


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers() -> list[ProviderInfo]:
    """Static catalog for the admin UI — lets it render Anthropic/OpenAI/Gemini
    as visibly disabled ("Not enabled") without hardcoding the allowlist
    client-side. `implemented` is the only thing that matters for whether a
    provider can actually be saved via PUT /config; see _SAVEABLE_PROVIDERS."""
    return [
        ProviderInfo(provider_type=p, implemented=p in _SAVEABLE_PROVIDERS) for p in sorted(_ALLOWED_PROVIDERS)
    ]


@router.put("", response_model=ConfigOut)
async def update_config(update: ConfigUpdate) -> ConfigOut:
    from app.api.errors import configuration_invalid

    if get_settings().deployment_mode == "demo":
        # P7: hosted demo is deterministic-only and offers nothing to
        # configure (D-05 stays open, no model provider is reachable from
        # the hosted deployment) — reject unconditionally rather than
        # relying on the frontend hiding the admin nav link, since the API
        # itself must not accept changes on a shared public host.
        raise configuration_invalid("Configuration changes are disabled in hosted demo mode.")

    if update.provider_type is not None:
        if update.provider_type not in _ALLOWED_PROVIDERS:
            raise configuration_invalid("provider_type must be one of the allowlisted providers.")
        if update.provider_type not in _SAVEABLE_PROVIDERS:
            raise configuration_invalid(
                f"provider_type '{update.provider_type}' is not yet implemented and cannot be "
                "saved as active configuration (D-05 is open). It is shown in the catalog as "
                "'Not enabled' only."
            )

    if update.base_url is not None:
        effective_provider = update.provider_type or _runtime_override["provider_type"] or get_settings().provider_type
        if effective_provider != "ollama":
            raise configuration_invalid(
                "base_url can only be set for the ollama provider; other providers' base URLs are fixed by backend code."
            )
        try:
            validate_ollama_base_url(update.base_url, get_settings().deployment_mode)
        except SsrfValidationError as exc:
            raise configuration_invalid(str(exc)) from None

    if update.provider_type is not None:
        _runtime_override["provider_type"] = update.provider_type
    if update.model_name is not None:
        _runtime_override["model_name"] = update.model_name
    if update.base_url is not None:
        _runtime_override["base_url_display"] = update.base_url
    if update.credential:
        _runtime_override["has_credential"] = True

    return await get_config()


@router.post("/test", response_model=ConfigTestResult)
async def test_config() -> ConfigTestResult:
    """Test the currently saved provider config (after any PUT /config).
    Only `ollama` has a real adapter and can be saved as active config as of
    P5 (see _SAVEABLE_PROVIDERS); any other provider_type is honestly
    reported as unavailable rather than faking a success, per the
    "Not enabled" convention in UI_SPEC.md."""
    settings = get_settings()
    provider_type = _runtime_override["provider_type"] or settings.provider_type
    model_name = _runtime_override["model_name"] or settings.model_name

    if provider_type != "ollama":
        raise errors.provider_unavailable()

    base_url = _runtime_override["base_url_display"] or settings.ollama_base_url
    adapter = OllamaAdapter(base_url=base_url, model_name=model_name, timeout_s=5.0)
    try:
        result = await adapter.ping()
    except ModelAdapterError:
        raise errors.provider_unavailable() from None

    return ConfigTestResult(ok=result.ok, provider_type=provider_type, model_name=model_name, latency_ms=result.latency_ms)
