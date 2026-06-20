# Production Safety

Production testing must prove impact without damaging confidentiality, integrity, availability, or cost controls.

## Stop Conditions

Stop the active tool or stage if any of these occur:

- 429/rate-limit waves
- Vercel or WAF challenges increase
- Error rates spike
- The app slows down noticeably
- A test would alter or delete real data
- A payload may trigger email/SMS/payment/AI cost
- The tool begins brute forcing credentials or tokens

## Evidence Rules

Prefer:

- HTTP status code
- Response headers
- Count of accessible rows
- Names of exposed columns
- Redacted body snippets
- Sanitized screenshots
- Canary record IDs

Avoid:

- Full dumps of clients, patients, leads, staff, orders, medical records, or payment data
- Plaintext passwords, cookies, JWTs, service role keys, refresh tokens
- Screenshots containing real private data

## "Most Violent" Requests

When the user asks for the strongest mode, explain the difference between depth and destructiveness. Offer Level 3 for production with canaries, or Level 4 in staging/lab with fake data.

Do not equate professionalism with maximum noise. A confirmed RLS bypass, auth bypass, IDOR, exposed admin endpoint, or unauthenticated data read is already high-quality evidence.

