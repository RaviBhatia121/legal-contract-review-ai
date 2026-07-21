# Part 2 Demo Runbook

## Purpose
This is the repeatable presentation path. Fill environment-specific values during implementation.

**Case-study narrative reminder (P7):** the hosted URL below is a synthetic demo
convenience only. It is not the target production architecture — the production
deployment target is fully on-premises (Docker-based Ollama/Qdrant, no cloud calls).
State this explicitly in the presentation (step 6 below) and never present the hosted
run as equivalent to, or a substitute for, the on-prem verification evidence.

**Local stack reliability note:** `backend`, `frontend`, and `ollama` run with
`restart: unless-stopped` in `docker-compose.yml`, so the local demo stack and Admin
`Test connection` path come back on their own if Docker restarts (e.g. after the host
reboots) — you should not normally need to run `docker compose up` again before a demo.
Review processing remains deterministic by default; Ollama being up only makes the optional
provider test available. If the stack is still down (e.g. Docker Desktop itself wasn't
running), fall back to `docker compose up -d --build` and re-check `docker compose ps`
before presenting.

## Demo Preconditions
- Hosted URL: `TBD` — the live Render deploy is **deferred to a later polish/optimization
  phase**, by explicit decision, not a P7 blocker. Fill this in once that phase runs
  `render.yaml` against `backend/Dockerfile.hosted`; the image itself is already built and
  verified locally, see `docs/SECURITY_EVIDENCE.md` §10
- Health endpoint: `/api/v1/health/live` (unauthenticated) or `/api/v1/health/ready`
  (requires the demo access credentials — see below)
- Demo user/access method: HTTP Basic Auth (`DemoBasicAuthMiddleware`), credentials set
  via `PART2_DEMO_ACCESS_USERNAME`/`PART2_DEMO_ACCESS_PASSWORD` in the Render dashboard,
  never committed; distribute the password to reviewers out-of-band, not in this doc
- Active model provider: none — the hosted demo is deterministic-only (P7, D-05 stays
  open); there is no Ollama or Qdrant reachable from the hosted environment
- Synthetic sample contract: `Sentinel Systems Support Services Agreement`
- Expected review result fixture: defined in `DEMO_FIXTURE_SPEC.md`; generated artifact `TBD`
- Demo-mode banner visible: yes — persistent, non-dismissible (`DemoModeBanner`), states
  synthetic-data-only and the on-prem production-target disclaimer
- Successful Docker Ollama local-model verification recorded: yes — 3 runs plus 1 egress-blocked run, `qwen3:4b`, see `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes
- Three-run local confidence and variance record: all 4 runs identical (High risk, 7 findings, confidence 0.9 throughout, zero variance)
- Hosted persistence: **ephemeral** (Render free plan, no persistent disk) — review
  records do not survive a redeploy/restart; acceptable because hosted data is synthetic
  and short-retention regardless. See `docs/OPEN_DECISIONS.md` D-07 and
  `docs/SECURITY_EVIDENCE.md` §10.

## Presentation Sequence
1. Open the Legal Review portal (hosted URL, behind the demo access prompt) and point out the structured workflow and the demo-mode banner.
2. Upload the synthetic sample contract.
3. Start the review and show the fixed processing stages.
4. Present overall risk, clause findings, missing clauses, evidence, and actions.
5. Note that `/admin/model` is intentionally not exposed on this hosted instance — the
   hosted demo is deterministic-only (P7). Switch to a local-mode screen-share or
   screenshots to show the admin configuration screen instead: Ollama as the only saveable
   provider, Anthropic/OpenAI/Gemini shown disabled in the catalog to demonstrate provider
   portability, and credentials never revealed.
6. Explain that the hosted URL is a synthetic demo convenience only — the target
   architecture runs entirely inside the enterprise environment using Docker-based Ollama
   (and, if retrieval is enabled, Qdrant) for the PoC validation path, with zero cloud
   calls. The hosted instance itself makes no model calls at all.
7. Close with the security and data-handling boundaries, including the hosted-only
   exceptions (Basic Auth access gate, ephemeral hosted storage) called out as demo-only,
   not production equivalents — see `docs/SECURITY_EVIDENCE.md` §10.
8. State that the playbook is illustrative decision support and requires client Legal validation for production.

## Failure Fallback
- Keep a known-good structured result fixture for UI demonstration.
- Keep screenshots of the successful end-to-end run.
- Do not represent fixture mode as a live model run.
- The fixed result is presentation continuity only and cannot satisfy final acceptance or the open-source-model utilization requirement.

## Post-Deployment Record
- Deployment date: `TBD`
- Commit/version: `TBD`
- Last successful smoke test: `TBD`
- Known limitations: `TBD`
