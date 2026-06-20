# Auth and Role Testing

Use this guide when the user provides test accounts, cookies, JWTs, or role descriptions.

## Inputs to Confirm

- Role name
- Test account email or identifier
- Whether the account contains only test data
- Expected permissions in plain business terms
- Session method: browser login, cookie, Bearer token, Supabase JWT
- Production/staging/local environment

Never store plaintext passwords in report files. If a token or cookie is needed temporarily, keep it in memory or a local temp file and remove it after checks.

## Role Matrix

Create a table with:

- Role
- Route or table
- Action: read, create, update, delete
- Expected result
- Observed result
- Evidence file
- Risk

Example:

| Role | Target | Action | Expected | Observed | Risk |
| --- | --- | --- | --- | --- | --- |
| vet | patients | read | own clinic patients | all patients | needs review |
| anon | clients | read | blocked | count visible | critical |

## Checks

Unauthenticated:

- Protected UI routes should redirect to login.
- Protected APIs should return 401/403 or redirect without data.
- Anonymous data-layer access should be blocked unless intentionally public.

Authenticated:

- Test one role at a time.
- Verify the role can do required work.
- Verify the role cannot see unrelated tenants, clinics, customers, patients, leads, invoices, or staff.
- Verify write actions only with canaries or invalid payloads.

Session handling:

- Check logout invalidates the web session.
- Check JWT expiration and refresh behavior only at a high level unless deeper testing is authorized.
- Do not brute force passwords, OTPs, magic links, or reset flows.

## Client-Side Controls

Treat UI-only restrictions as informational until the server is tested. If the browser hides a button but the API accepts the action, that is a real authorization issue.

Examples:

- Login attempt counters must be enforced server-side.
- Role menus must not be the only access control.
- Hidden routes must still require authorization.

## Evidence Hygiene

Save:

- Status codes
- Redirect targets
- Counts
- Redacted JSON keys
- Sanitized screenshots

Do not save:

- Full JWTs
- Cookies
- Passwords
- Full PII records
- Medical, financial, or client details

