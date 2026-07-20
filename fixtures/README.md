Synthetic contract fixtures were added in P1 (real document parsing). See
`docs/DEMO_FIXTURE_SPEC.md` for the required fixture files and expected JSON.
As of P2, `sentinel-support-agreement.expected.json` reflects the deterministic
rule-engine target output using canonical playbook clause types.

Additional manual-test fixtures were added after P3 for browser/UAT coverage:
- `compliant-defense-services-agreement.pdf` / `.docx` — happy-path agreement;
  expected deterministic summary: `Low`, no Critical/High/Medium findings, no
  missing clauses, no needs-review items.
- `nusantara-enterprise-master-services-agreement.pdf` / `.docx` — longer
  organization-style master services agreement; expected deterministic summary:
  `High`, no Critical findings, no missing clauses, no needs-review items.

Regenerate the additional fixtures with
`python scripts/generate_additional_test_contracts.py` from the repo root.
