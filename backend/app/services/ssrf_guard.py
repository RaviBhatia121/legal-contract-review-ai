"""SSRF validation for the admin-configurable Ollama `base_url` (P6).

This is a blocklist-first check, not a strict default-deny allowlist: only
specific dangerous ranges are always rejected, plus a mode-gated
restriction on private (RFC1918) ranges. Loopback and the fixed hostnames
below are always allowed regardless of deployment mode.

Do NOT read this as "private IPs are safe" — the R-07 mitigation is
deliberately scoped:
- always allowed: `localhost`, `127.0.0.1`, the Docker Compose service name
  `ollama`, and the whole loopback range (127.0.0.0/8, ::1)
- always blocked: link-local (169.254.0.0/16, including the
  169.254.169.254 cloud-metadata address that is the single most common
  real-world SSRF target), multicast, reserved, and unspecified ranges,
  plus their IPv6 equivalents
- private RFC1918 ranges (10/8, 172.16/12, 192.168/16) are allowed ONLY in
  `deployment_mode: local` — this is exactly where the `ollama` Compose
  service and other on-prem infrastructure legitimately live, but the same
  trust is not extended to hosted Demo mode
- any other public address is allowed by default (not the concern this
  check exists for); full enterprise egress-policy allowlisting is P7 scope
"""

import ipaddress
import socket
from urllib.parse import urlparse

_ALLOWED_HOSTNAMES = {"localhost", "ollama"}

_ALWAYS_BLOCKED_NETWORKS = [
    ipaddress.ip_network("169.254.0.0/16"),  # IPv4 link-local, incl. cloud metadata 169.254.169.254
    ipaddress.ip_network("224.0.0.0/4"),  # IPv4 multicast
    ipaddress.ip_network("240.0.0.0/4"),  # IPv4 reserved
    ipaddress.ip_network("0.0.0.0/8"),  # "this network" / unspecified
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("ff00::/8"),  # IPv6 multicast
]

_LOOPBACK_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
]

_LOCAL_MODE_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


class SsrfValidationError(Exception):
    """Raised with a message safe to return to the API caller — never
    includes internal topology beyond what the admin themselves submitted."""


def validate_ollama_base_url(url: str, deployment_mode: str) -> None:
    """Raises SsrfValidationError if `url` is not safe to configure as the
    Ollama base URL. Does nothing (returns) if it is safe."""
    try:
        parsed = urlparse(url)
    except ValueError:
        raise SsrfValidationError("base_url must be a valid http:// or https:// URL with a hostname.") from None

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SsrfValidationError("base_url must be a valid http:// or https:// URL with a hostname.")

    hostname = parsed.hostname.lower()
    if hostname in _ALLOWED_HOSTNAMES:
        return

    try:
        resolved = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        raise SsrfValidationError("base_url hostname could not be resolved.") from None

    for _family, _type, _proto, _canonname, sockaddr in resolved:
        ip = ipaddress.ip_address(sockaddr[0])

        if any(ip in net for net in _ALWAYS_BLOCKED_NETWORKS):
            raise SsrfValidationError(
                "base_url resolves to a link-local, multicast, reserved, or unspecified address, which is never allowed."
            )
        if any(ip in net for net in _LOOPBACK_NETWORKS):
            continue
        if any(ip in net for net in _LOCAL_MODE_PRIVATE_NETWORKS):
            if deployment_mode != "local":
                raise SsrfValidationError(
                    "base_url resolves to a private network address, which is only permitted in local deployment mode."
                )
            continue
        # Any other (public) address is allowed — this check targets the
        # specific dangerous ranges above, not general egress policy.
