---
name: security-review-levels
description: Authorized security review and pentest workflow for web apps, SaaS, CRM systems, landing pages, Next.js/Vercel/Supabase projects, APIs, and chatbot widgets. Use when Codex must plan or run a defensive assessment by depth level, choose safe tools, avoid destructive production actions, collect evidence, summarize findings in plain language, or generate a final report with fixes.
---

# Security Review Levels

## Core Rule

Run only authorized defensive testing. Match test depth to the target environment and stop before destructive impact. Demonstrate risk with safe evidence, canary records, metadata, counts, headers, status codes, and sanitized screenshots instead of exposing, modifying, deleting, or dumping real sensitive data.

## Workflow

1. Confirm scope: target URLs, environment, authorization, allowed windows, test accounts, and whether production is in scope.
2. Choose a depth level from `references/levels.md`.
3. Check tools with `scripts/check_tools.py`.
4. Create a report workspace with `scripts/init_assessment.py`.
5. Optionally plan or run staged commands with `scripts/run_assessment.py`; it writes a dry-run plan unless `--execute` is provided.
6. Read and summarize evidence after each stage in simple terms: normal, review, fix now.
7. Sanitize secrets, tokens, passwords, cookies, screenshots with real data, and PII before final output.
8. Produce a report using `references/report-template.md` or `scripts/generate_report.py`.

## Mandatory Safety Gates

For production:

- Do not run credential brute force, password spraying, denial-of-service, destructive payloads, or high-volume fuzzing.
- Do not run SQL injection tools above low risk/low level unless the user explicitly confirms and the endpoint uses canary data.
- Do not create, update, or delete real records. Use canaries or invalid bodies that prove authorization behavior without changing state.
- If a tool begins causing rate limits, Vercel challenges, cost spikes, or instability, stop that tool and record the partial result.

For staging or local environments with fake data:

- Deeper fuzzing and higher scanner intensity are allowed if the user confirms the environment contains no real customer/patient/client data.
- Destructive proof still requires explicit confirmation and a rollback plan.

## Resource Routing

- Read `references/levels.md` before selecting tools or intensity.
- Read `references/production-safety.md` when the target is production or the user asks for the “strongest,” “most violent,” or deepest mode.
- Read `references/supabase-nextjs.md` for Next.js, Vercel, Supabase, RLS, anon key, JWT, CORS, auth, and role testing.
- Read `references/auth-roles.md` when test accounts, cookies, JWTs, or role matrices are in scope.
- Read `references/tool-recipes.md` when choosing concrete commands for common tools.
- Use Level 5 from `references/levels.md` when the user asks for enterprise-grade assurance, reusable security programs, CI security gates, retesting, or executive reporting.
- Read `references/report-template.md` when producing a final Markdown, HTML, or PDF report.

## Stage Guidance

Recon:

- Use DNS/HTTP/TLS/technology fingerprinting and low-noise port checks.
- Prefer `nmap` 80/443 first for cloud hosts, then broaden only when justified.

Content discovery:

- Use crawlers and wordlists at a rate appropriate to the level.
- For production, prefer discovered links, sitemap, robots, JS route extraction, and low-rate directory checks.

App/auth:

- Check unauthenticated protected routes, redirects, CORS, headers, rate limiting signals, and role boundaries.
- Use provided test accounts only. Do not try real user credentials.

Data layer:

- For Supabase, treat public anon keys as expected but RLS as mandatory.
- Test anonymous read/write/update/delete behavior safely. Save counts and column names, not real sensitive values.

Vulnerability scanners:

- Run scanners stage by stage, not all at once.
- Capture partial outputs and explain false positives separately from confirmed issues.

Reporting:

- Findings must include impact, evidence path, severity, and concrete fix.
- Lead with confirmed critical issues, then review items, then normal findings.

## Bundled Scripts

- `scripts/check_tools.py --level N`: list installed and missing tools for a depth level.
- `scripts/init_assessment.py NAME --level N`: create a clean evidence/report directory.
- `scripts/run_assessment.py URL --level N`: write a staged command plan; add `--execute` to run safe commands.
- `scripts/generate_report.py resumen.md`: create sanitized HTML/PDF from a Markdown summary.
