"""Approved-template drafting support for Legal findings.

This is deliberately deterministic: rule ids map to pre-approved template
language. It is not free-form generation and does not change risk decisions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DraftClause:
    text: str
    source: str = "approved_template"
    approval_note: str = "Drafting support only; legal approval required before use."


_TEMPLATES: dict[str, str] = {
    "CONF-001": (
        "Supplier shall not disclose Confidential Information except to personnel and approved representatives "
        "with a strict need to know and written obligations no less protective than this Agreement."
    ),
    "CONF-002": (
        "Supplier may disclose Confidential Information only to approved representatives with a need to know, "
        "provided each recipient is bound by written confidentiality obligations at least as protective as this Agreement."
    ),
    "CONF-003": (
        "Add a mutual confidentiality clause covering protected information, permitted recipients, need-to-know access, "
        "equivalent written obligations, survival, and return or destruction on request."
    ),
    "DATA-001": (
        "Supplier shall process and store Customer Data only within Buyer-approved, client-controlled environments and "
        "shall not use public cloud or external processing locations without Buyer's prior written approval."
    ),
    "DATA-002": (
        "Supplier shall document data location, retention, return, verified deletion, and transfer controls before "
        "processing Customer Data and shall comply with Buyer's written data-handling instructions."
    ),
    "DATA-003": (
        "Supplier shall not transfer Customer Data cross-border without Buyer's prior written approval and a documented "
        "lawful transfer basis acceptable to Buyer."
    ),
    "DATA-004": (
        "Add a data-handling clause covering approved locations, retention, return, verified deletion, transfer limits, "
        "and Buyer auditability of data-processing controls."
    ),
    "SUB-001": (
        "Supplier shall not appoint subcontractors or permit subcontractor access to services, systems, or Sensitive Data "
        "without Buyer's prior written approval."
    ),
    "SUB-002": (
        "Supplier shall flow down equivalent security, confidentiality, audit, data-protection, and compliance obligations "
        "to each approved subcontractor and remain liable for subcontractor acts and omissions."
    ),
    "SUB-003": (
        "Add subcontracting controls requiring prior written approval, equivalent flow-down obligations, and Supplier "
        "responsibility for all approved subcontractors."
    ),
    "AUD-001": (
        "Buyer may conduct reasonable risk-based audits, inspections, and evidence reviews of Supplier controls relevant "
        "to the services, subject to confidentiality and operational safeguards."
    ),
    "AUD-002": (
        "Supplier shall provide independent evidence or assessment materials sufficient for Buyer to validate relevant "
        "security, privacy, operational, and compliance controls."
    ),
    "IP-001": (
        "Buyer owns all bespoke deliverables created specifically for Buyer, excluding Supplier Background IP, which may "
        "be used only as needed under the license expressly granted in this Agreement."
    ),
    "IP-002": (
        "Supplier retains Background IP, but grants Buyer a perpetual, irrevocable, worldwide, royalty-free license to "
        "use embedded Background IP as necessary to use, maintain, and exploit the deliverables."
    ),
    "IP-003": (
        "Add intellectual-property terms defining bespoke deliverable ownership, Background IP, license scope, and "
        "restrictions on reuse of Buyer-specific materials."
    ),
    "LIAB-001": (
        "Liability caps shall not apply to confidentiality breaches, data-security incidents, intellectual-property "
        "infringement, fraud, willful misconduct, or other uncapped obligations expressly agreed by the parties."
    ),
    "LIAB-002": (
        "Supplier shall defend, indemnify, and hold Buyer harmless from third-party claims alleging that Supplier-provided "
        "materials, services, or deliverables infringe intellectual-property rights."
    ),
    "LIAB-003": (
        "Add liability and indemnity terms with appropriate carve-outs for confidentiality, security, IP infringement, "
        "fraud, willful misconduct, and third-party claims."
    ),
    "TERM-001": (
        "Buyer may terminate this Agreement or affected services for Supplier's uncured material breach after written "
        "notice and any agreed cure period."
    ),
    "TERM-002": (
        "On termination or expiry, Supplier shall return Customer Data, securely delete remaining copies, certify deletion, "
        "and provide reasonable transition assistance."
    ),
    "TERM-003": (
        "Add termination and exit terms covering material breach, security events, data return, verified deletion, and "
        "transition assistance."
    ),
    "TERM-004": (
        "Retain the termination and exit wording, subject to Legal validation that data return, verified deletion, and "
        "transition assistance obligations are operationally enforceable."
    ),
    "SEC-001": (
        "Supplier shall maintain the approved security schedule, including access control, encryption, logging, vulnerability "
        "management, incident response, and evidence obligations."
    ),
    "SEC-002": (
        "Supplier shall notify Buyer of security incidents without undue delay and no later than 24 hours after awareness, "
        "with continuing updates until containment and remediation are complete."
    ),
    "SEC-003": (
        "Supplier shall maintain documented administrative, technical, and physical safeguards appropriate to the services "
        "and Buyer data, subject to Legal and security validation."
    ),
    "SEC-004": (
        "Add a security and incident-response clause covering minimum safeguards, incident notification timelines, evidence "
        "support, remediation cooperation, and post-incident reporting."
    ),
    "REV-001": (
        "Route the clause and evidence to Legal review before relying on automated output; do not treat uncertain "
        "classification as approval or compliance."
    ),
}


def draft_clause_for_rule(rule_id: str) -> DraftClause | None:
    text = _TEMPLATES.get(rule_id)
    if text is None:
        return None
    return DraftClause(text=text)
