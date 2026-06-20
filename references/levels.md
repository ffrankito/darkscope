# Depth Levels

Use the lowest level that can answer the user's question. Increase depth only with authorization, clear scope, and a reason.

## Level 0 - Passive Orientation

Purpose: understand the system without touching it heavily.

Use:

- User wants a first look.
- Scope is unclear.
- Production authorization is not explicit.

Tools:

- Browser/manual review
- `curl`
- `whatweb`
- DNS/TLS metadata
- Public JS inspection

Do not:

- Fuzz
- Run vulnerability scanners
- Authenticate with real users unless provided as test accounts

## Level 1 - Safe Production Baseline

Purpose: low-noise verification of common exposure and misconfiguration.

Tools:

- `nmap` limited to web ports unless justified
- `whatweb`, `wafw00f`, `sslscan`
- `curl`, `jq`
- `katana` or equivalent crawler at low rate
- Header/CORS checks
- Known-route checks

Acceptable:

- Read-only endpoint checks
- Login page inspection
- Public API OPTIONS/GET checks

Avoid:

- Broad gobuster/ffuf
- SQLMap
- Nuclei full template set

## Level 2 - Standard Authorized Production

Purpose: practical production pentest without destructive behavior.

Tools:

- Level 1 tools
- `nikto`
- `nuclei` severity medium/high/critical or targeted templates
- `gitleaks`, `trufflehog` on downloaded public artifacts
- `feroxbuster`/`ffuf` low rate with small wordlists
- `ZAP` passive/baseline/recon
- Playwright/Selenium UI checks with test accounts
- Supabase/PostgREST RLS checks when applicable

Acceptable:

- Invalid-body write probes that do not create records
- Canary reads/writes only when user confirms canary identifiers
- Authenticated role checks with provided test accounts

Avoid:

- High-risk SQLMap
- Credential brute force
- High-volume fuzzing
- Real data modification/deletion

## Level 3 - Deep Controlled Testing

Purpose: stronger coverage while still protecting production.

Best target:

- Staging, local, or production with canaries and explicit written approval.

Tools:

- Level 2 tools
- Broader `nuclei`
- Broader `ffuf`/`feroxbuster`
- `sqlmap --level=1 --risk=1` first, increasing only on canary endpoints
- API schema fuzzing with rate limits
- Role matrix tests
- Business logic abuse tests

Required gates:

- Confirm target is not handling real destructive operations.
- Confirm canary records.
- Confirm stop conditions.

## Level 4 - Aggressive Lab/Staging

Purpose: simulate a determined attacker without risking real users.

Use only for:

- Local/staging/lab environments with fake data.
- Explicit approval for high intensity.

Tools:

- Full-template scanner runs
- Large wordlists
- Higher SQLMap risk/level on fake data
- Auth/session abuse tests
- Controlled destructive canary tests
- Load/cost-abuse simulation with strict caps

Never run on production with real data unless the user gives explicit approval, a rollback plan exists, and the action is limited to canary records.

## Level 5 - Enterprise Assurance

Purpose: turn the assessment into a repeatable security program, not only a one-time scan.

Best target:

- Production plus staging plus source code plus cloud/security configuration.
- Requires clear owners, retest window, and remediation tracking.

Includes:

- Level 3 production-safe testing.
- Level 4 aggressive testing only in staging/lab with fake data.
- Source code review for auth, tenant isolation, RLS, secrets, CORS, webhooks, cron jobs, payments, AI/chatbot cost controls, and audit logs.
- Role matrix for every business role.
- Data classification and PII/PHI inventory.
- Threat model for main workflows.
- CI security gates: dependency scan, Semgrep/custom rules, secret scanning, and security regression tests.
- Evidence package with sanitized artifacts, severity, owner, due date, and retest result.
- Executive summary plus technical appendix.

Required gates:

- Written scope and exclusions.
- Test accounts for every role.
- Canary data plan.
- Staging/lab environment for destructive or high-volume tests.
- Retest after fixes.

Enterprise success criteria:

- No anonymous access to private data.
- No role can read or mutate data outside its business need.
- Public endpoints have rate limits, logging, and abuse controls.
- Security tests can be rerun after every release.
- Critical/high findings have owners and deadlines.
