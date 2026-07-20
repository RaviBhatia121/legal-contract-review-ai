"""SSRF validation tests (P6/R-07) for the admin-configurable Ollama base_url.

Blocklist-first design: specific dangerous ranges are always rejected;
private RFC1918 ranges are only allowed in `deployment_mode: local`; fixed
hostnames and loopback are always allowed. See ssrf_guard.py's module
docstring for the full rationale."""

import pytest

from app.services.ssrf_guard import SsrfValidationError, validate_ollama_base_url


def test_allows_ollama_hostname_in_local_mode():
    validate_ollama_base_url("http://ollama:11434", "local")


def test_allows_ollama_hostname_in_demo_mode():
    # Fixed hostnames are always allowed, regardless of deployment mode —
    # they don't depend on the mode-gated private-range check.
    validate_ollama_base_url("http://ollama:11434", "demo")


def test_allows_localhost_in_any_mode():
    validate_ollama_base_url("http://localhost:11434", "local")
    validate_ollama_base_url("http://localhost:11434", "demo")


def test_allows_loopback_ip_in_any_mode():
    validate_ollama_base_url("http://127.0.0.1:11434", "local")
    validate_ollama_base_url("http://127.0.0.1:11434", "demo")


def test_allows_private_range_in_local_mode():
    validate_ollama_base_url("http://192.168.1.50:11434", "local")
    validate_ollama_base_url("http://10.0.0.5:11434", "local")
    validate_ollama_base_url("http://172.20.0.5:11434", "local")


def test_rejects_private_range_in_demo_mode():
    with pytest.raises(SsrfValidationError, match="only permitted in local deployment mode"):
        validate_ollama_base_url("http://192.168.1.50:11434", "demo")


def test_rejects_link_local_metadata_address_in_any_mode():
    # The classic cloud-metadata SSRF target — must never be allowed,
    # local mode or not.
    with pytest.raises(SsrfValidationError, match="link-local"):
        validate_ollama_base_url("http://169.254.169.254/", "local")
    with pytest.raises(SsrfValidationError, match="link-local"):
        validate_ollama_base_url("http://169.254.169.254/", "demo")


def test_rejects_multicast_address():
    with pytest.raises(SsrfValidationError, match="multicast"):
        validate_ollama_base_url("http://224.0.0.1:11434", "local")


def test_rejects_reserved_address():
    with pytest.raises(SsrfValidationError, match="reserved"):
        validate_ollama_base_url("http://240.0.0.1:11434", "local")


def test_rejects_unresolvable_hostname():
    with pytest.raises(SsrfValidationError, match="could not be resolved"):
        validate_ollama_base_url("http://this-host-does-not-exist.invalid:11434", "local")


def test_rejects_invalid_scheme():
    with pytest.raises(SsrfValidationError, match="http:// or https://"):
        validate_ollama_base_url("javascript:alert(1)", "local")


def test_allows_public_address_by_default():
    # Not the concern this check exists for — only the specific dangerous
    # ranges above are blocked; a legitimate remote Ollama on a public IP
    # (e.g. a self-hosted VPS) is allowed.
    validate_ollama_base_url("http://8.8.8.8:11434", "local")
    validate_ollama_base_url("http://8.8.8.8:11434", "demo")
