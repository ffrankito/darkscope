# Tool Recipes

Commands are examples. Adjust target, rate, and output paths for scope and level.

## Recon

Headers:

```bash
curl -sk -D - -o /dev/null "$TARGET"
```

Technology fingerprint:

```bash
whatweb -a 3 "$TARGET"
```

WAF:

```bash
wafw00f "$TARGET"
```

Web ports only:

```bash
nmap -sV -sC -Pn -p 80,443 "$HOST"
```

TLS:

```bash
sslscan "$HOST"
```

## Content Discovery

Crawler:

```bash
katana -u "$TARGET" -d 2 -silent
```

Low-rate feroxbuster for production:

```bash
feroxbuster -u "$TARGET" -k -x js,json,txt -t 5 --rate-limit 5 -w /usr/share/wordlists/dirb/common.txt
```

Low-rate ffuf:

```bash
ffuf -u "$TARGET/FUZZ" -w /usr/share/wordlists/dirb/common.txt -rate 5 -mc 200,204,301,302,307,401,403
```

## Vulnerability Scanners

Nikto:

```bash
nikto -h "$TARGET"
```

Nuclei priority templates for production:

```bash
nuclei -u "$TARGET" -severity medium,high,critical -silent
```

ZAP quick recon:

```bash
/usr/share/zaproxy/zap.sh -cmd -zapit "$TARGET"
```

SQLMap low risk only:

```bash
sqlmap -u "$TARGET/api/example?id=1" --batch --level 1 --risk 1 --smart
```

Do not raise SQLMap risk/level against production unless the endpoint uses canary data and the user explicitly approves it.

## Secrets in Public Artifacts

Gitleaks:

```bash
gitleaks detect --source "$ARTIFACT_DIR" --no-git --report-format json --report-path "$OUT/gitleaks.json"
```

TruffleHog:

```bash
trufflehog filesystem "$ARTIFACT_DIR" --json
```

## Supabase REST Checks

Anonymous read count:

```bash
curl -sk "$SUPABASE_URL/rest/v1/$TABLE?select=id&limit=1" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ANON_KEY" \
  -H "Prefer: count=exact"
```

Invalid-body insert probe:

```bash
curl -sk -X POST "$SUPABASE_URL/rest/v1/$TABLE" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected safe result for sensitive tables: 401/403 or RLS denial before schema/constraint errors.

