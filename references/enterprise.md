# Enterprise Assurance

Use this reference for Level 5.

## Deliverables

- Executive report
- Technical appendix
- Evidence index
- Role matrix
- Data exposure matrix
- Remediation tracker
- Retest report
- CI/security gate recommendations

## Security Gates

CI should fail or warn on:

- New secrets in repository or build artifacts
- Critical/high dependency vulnerabilities
- RLS policy tests failing
- Protected route tests failing
- Public API rate limit tests failing
- Missing required security headers
- Unsafe CORS on sensitive endpoints

## Ownership

Every critical/high finding needs:

- Owner
- Due date
- Fix plan
- Retest step
- Regression test

## Evidence Quality Bar

Enterprise evidence should prove:

- Who can exploit it
- What data/action is exposed
- Whether auth is required
- Whether it crosses tenant/role boundaries
- How to reproduce safely
- How to fix
- How to verify the fix

## Retest

After fixes:

- Rerun the exact failing checks.
- Add one negative test proving blocked access.
- Add one positive test proving intended access still works.
- Update status to fixed only after evidence confirms it.

## Risk Language

Use plain impact language:

- Critical: unauthenticated or wrong-role access to private data, destructive actions, auth bypass, service role exposure, account takeover.
- High: sensitive authenticated overreach, missing tenant isolation, write access beyond role, exploitable injection without destructive proof.
- Medium: missing rate limits, weak headers, broad CORS on non-sensitive endpoints, information disclosure.
- Low: hardening gaps with limited direct impact.
- Informational: expected exposure or normal behavior.
