# Supabase + Next.js Checklist

## Public Frontend Artifacts

Check downloaded JS for:

- Supabase project URL
- anon JWT
- route names
- API paths
- feature flags
- storage buckets
- hardcoded test credentials

The Supabase anon key being public is expected. The security boundary is RLS and policies.

## Supabase REST RLS Checks

For each sensitive table:

- Anonymous `SELECT` should fail or return only intentionally public rows.
- Anonymous `INSERT` should fail unless it is a public intake table.
- Anonymous `UPDATE` and `DELETE` should fail.
- Authenticated role access should match the business role matrix.

Safe evidence:

- `select=id&limit=1`
- `Prefer: count=exact`
- column names from a single limited row, redacted
- invalid-body write probes that do not create rows
- nonexistent-ID update/delete probes

Do not:

- Dump full tables
- Store raw PII in reports
- Use service role keys from frontend or user chat

## Next.js / Vercel Checks

Check:

- Protected route redirects without session
- API routes with and without cookies
- Whether Bearer JWT alone is accepted
- Middleware behavior
- `X-Powered-By`
- CSP, clickjacking, content-type, referrer, permissions headers
- CORS per endpoint
- Source maps and public chunks

## Role Testing

For each provided test role:

- Decode JWT metadata without saving raw token.
- Test only read permissions unless canaries are authorized.
- Build a role/table/action matrix.
- Mark "expected broad access" separately from "confirmed anonymous access."

