```
 ____            _     ____                   
|  _ \  __ _ _ _| |_  / ___|  ___ ___  _ __  
| | | |/ _` | '__| __| \___ \ / __/ _ \| '_ \ 
| |_| | (_| | |  | |_   ___) | (_| (_) | |_) |
|____/ \__,_|_|   \__| |____/ \___\___/| .__/ 
                                       |_|    
```

**Authorized Security Assessment Framework**

![Status](https://img.shields.io/badge/Status-Production%20Ready-000?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-000?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-000?style=flat-square)
![Free](https://img.shields.io/badge/Cost-Free-000?style=flat-square)

[GitHub](https://github.com/ffrankito/darkscope) · [Docs](QUICKSTART.md) · [Architecture](ARCHITECTURE.md)

---

## Overview

DarkScope is a **modular pentesting framework** that automates security assessment phases while maintaining strict safety boundaries. Designed for authorized assessments on production and staging environments.

**No commercial tools required.** All integrations use free/open-source security tools (nmap, nikto, nuclei, sqlmap, etc.)

### What DarkScope Does

| Phase | Tools | What You Get |
|-------|-------|--------------|
| Reconnaissance | nmap, whatweb, wafw00f, sslscan | Headers, tech stack, WAF, SSL config |
| Discovery | ffuf, feroxbuster, katana | Routes, endpoints, JavaScript analysis |
| Vulnerability Scanning | nikto, nuclei, zap | Web app vulns, template-based detection |
| SQL Testing | sqlmap, manual payloads | SQL injection, database fingerprinting |
| Code Analysis | semgrep, trivy, npm audit, pip audit | SAST, CVE scanning, dependency auditing |
| Supabase Testing | Custom probes | RLS bypass, JWT validation, CORS config |
| Plugin System | Custom checks | Org-specific security rules |

**Output:** Sanitized findings JSON → HTML/PDF reports → Interactive dashboard → Baseline tracking

### What DarkScope Doesn't Do

- ❌ Destructive testing (no data modification/deletion)
- ❌ Credential attacks (no brute force, password spray)
- ❌ DOS attacks
- ❌ Anything without explicit authorization
- ❌ Automatic remediation (findings only)

---

## Installation

```bash
$ git clone https://github.com/ffrankito/darkscope.git
$ cd darkscope
$ pip install -r requirements.txt
$ python3 scripts/check_tools.py --level 2 --auto-install
```

**Dependencies:** Python 3.11+, curl, jq  
**Tools:** Auto-detected and installed (nmap, nikto, nuclei, etc. optional)

## Usage

### Dry-run (view plan without executing)
```bash
$ python3 scripts/run_assessment.py https://target.com --level 2
# Generates run_plan.txt with all commands that would execute
```

### Execute Assessment (Level 2: Standard Production)
```bash
$ python3 scripts/run_assessment.py https://target.com \
    --level 2 \
    --authorized \
    --execute
```

**Output:**
```
results/target.com_20260621_120000/
├── findings.json          # Machine-readable
├── report.html            # Human-readable
├── report.pdf             # Stakeholder report (L5+)
├── comparison.json        # Delta vs prior
├── assessment.log         # Audit trail
└── darkscope_auth_logs/
    └── auth_*.txt         # Authorization proof
```

### Generate Reports
```bash
$ python3 scripts/generate_report_v2.py results/findings.json \
    --output-pdf report.pdf --level 5

$ python3 scripts/dashboard.py results --output dashboard.html
open dashboard.html
```

### Track Progress (Baseline Comparison)
```bash
$ python3 scripts/compare_baselines.py \
    --current new_results/findings.json \
    --prior old_results/findings.json
```

**Output:**
```
Fixed:        5 ✓
New:          2
Regressions:  0
Health Trend: IMPROVING
```

---

## Assessment Levels (0-5)

| Level | Use Case | Tools | Scope |
|-------|----------|-------|-------|
| **0** | First look | whatweb, curl | Passive fingerprinting |
| **1** | Prod baseline | +nmap, +sslscan | Network recon |
| **2** | Standard (typical) | +nikto, +nuclei | Web app testing |
| **3** | Deep staging | +sqlmap, +semgrep | SQL, code analysis |
| **4** | Lab attack | +zap active | Full exploitation |
| **5** | Enterprise CI | All tools | Automated tracking |

**Key:** Level 2 is production-safe. Higher levels require staging/lab environments. Level 5 is safest but most comprehensive (no destructive payloads, just broad coverage).

---

## What It Tests

### reconnaissance.py
```
nmap -sV -Pn -p 80,443,8080,8443
whatweb -a 3
wafw00f -a
sslscan
HTTP header validation (CSP, HSTS, X-Frame-Options, etc.)
```

### discovery.py
```
ffuf + feroxbuster (directory enumeration)
katana (full crawl)
JavaScript route extraction
API endpoint discovery
```

### vulnerability_scanning.py
```
nikto (CMS vulns, headers, server vulns)
nuclei (template-based scanning)
zap (active scanning)
```

### sql_testing.py
```
Manual SQLi on common parameters
sqlmap aggressive testing (L4+)
Error-based detection
Database fingerprinting
```

### code_analysis.py
```
semgrep (OWASP Top 10, code patterns)
npm audit / pip audit (dependency vulns)
trivy (CVE scanning)
```

### probe_supabase.py (Supabase-specific)
```
RLS testing: SELECT/INSERT/UPDATE/DELETE on anon role
JWT inspection (claims, expiration, metadata)
CORS wildcard detection
Per-table findings
```

---

## Real Example: NeoVet CRM

Veterinary clinic running Supabase + Next.js. DarkScope found:

```
Assessment: neo-vet-eta.vercel.app
Level: 2 (Standard Production)
Date: 2026-06-20

🚨 CRITICAL (1)
  ❌ Supabase: patients table readable by anonymous users
     32 patient records exposed (DNI, phone, medical history visible)
     Fix: CREATE POLICY patients_read ON patients 
            FOR SELECT USING (auth.uid() = user_id);

⚠️  HIGH (3)
  ⚠️  Missing X-Frame-Options header (clickjacking risk)
  ⚠️  CORS: Access-Control-Allow-Origin: * (overly broad)
  ⚠️  /api/chat rate limit not enforced (cost amplification risk)

🟡 MEDIUM (2)
  ...

Report Generated: results/report.pdf
Dashboard: open results/dashboard.html
Health Score: 45% → CRITICAL
```

**Team response:**
- Fixed RLS policy in 2 hours
- Added headers in 30 minutes
- Implemented rate limit in 4 hours
- **Re-tested** with DarkScope → 0 regressions
- Dashboard shows progression: 45% → 92% health

---

## Key Features

### 🔐 Evidence Sanitization
Automatically redacts PII:
```
Emails → [EMAIL]
Phone numbers → [PHONE]
JWT/API keys → [JWT], [API_KEY]
Database URLs → [DATABASE_URL]
Credit cards → [CREDIT_CARD]
```

Why: Reports go to non-security staff. Real customer data = compliance nightmare.

### 📋 Authorization Audit
```
darkscope_auth_logs/auth_20260620_114022.txt

Status:       APPROVED
Target:       https://target.com
Level:        2 (Standard Production)
Timestamp:    2026-06-20T11:40:22
User:         franco
Hostname:     mymachine.local

✓ Proof of authorization for compliance
```

### 📊 Baseline Tracking
```bash
$ python3 scripts/compare_baselines.py \
  --current results.json --prior prior_results.json

Fixed:          5 ✅
New:            2 🆕
Regressions:    0 ⚠️
Improvements:   3 📈

Critical Count: 3 → 1 (-2) ✅
Health Trend:   IMPROVING 📈
```

### 🔌 Plugin System
Add org-specific checks:

```python
# plugins/my_checks.py
from plugin_manager import DarkScopePlugin

class MySecurityChecks(DarkScopePlugin):
    name = "My Compliance Checks"
    level_required = 2
    
    def run(self, target, **kwargs):
        return [
            {
                'title': 'Custom finding',
                'severity': 'HIGH',
                'evidence': {...},
                'recommendation': '...'
            }
        ]
```

Plugins auto-load. Zero registration.

### 🤖 CI/CD Automation
```yaml
# .github/workflows/darkscope.yml
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly Sunday 2 AM UTC
```

Auto-generates:
- Artifacts (reports, findings)
- Slack notifications (critical findings)
- GitHub issues (auto-remediation tracking)
- Health score trends

---

## Comparison

| Feature | DarkScope | Burp Suite | OWASP ZAP | Manual Pentesting |
|---------|-----------|-----------|-----------|---------|
| Cost | Free | $$$ | Free | Time ($$$$) |
| Repeatable | ✅ | ✅ | ✅ | ❌ |
| Evidence sanitization | ✅ | ❌ | ❌ | ❌ |
| Baseline tracking | ✅ | ❌ | ❌ | ❌ |
| Authorization audit log | ✅ | ❌ | ❌ | ❌ |
| CI/CD integration | ✅ | Manual | Manual | ❌ |
| Plugin system | ✅ | ❌ | ✅ | N/A |
| Safe on production | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Supabase native | ✅ | ❌ | ❌ | Manual |

---

## Security Guarantees

✅ **DarkScope WILL:**
- Detect misconfigured RLS policies
- Find exposed routes and endpoints
- Check auth/authz (with provided credentials)
- Validate security headers
- Test CORS configuration
- Detect common web vulns (safe probes)

❌ **DarkScope will NOT:**
- Brute force credentials
- Password spray
- Denial-of-service
- Modify real data
- Delete or corrupt anything
- Exploit vulnerabilities

**Authorization is mandatory.** Every assessment logged.

---

## 💰 Free & Open Source

**DarkScope is 100% FREE. No hidden costs. No paid features.**

- ✅ **Free forever** — MIT license, use commercially
- ✅ **No subscriptions** — Own your security testing
- ✅ **All tools included** — nmap, nuclei, nikto, etc. (all free/open source)
- ✅ **No paywalls** — Full features at no cost
- ✅ **Community-driven** — GitHub issues, contributions welcome

All external tools DarkScope uses are also **free and open source**:
- `nmap` — Open source network mapper
- `nikto` — Free web server scanner
- `nuclei` — Open source template scanner
- `feroxbuster` — Free directory enumerator
- `semgrep` — Free static analysis
- `trivy` — Open source vulnerability scanner

**Optional** (but also free):
- `weasyprint` — Free PDF generation (for HTML→PDF reports)
- `pip audit` — Free Python vulnerability scanning
- `npm audit` — Free Node.js vulnerability scanning

---

## FAQ

**Q: Can DarkScope break production?**  
A: No. It only reads (SELECT probes use invalid IDs). Zero writes.

**Q: How do I know it's safe?**  
A: Authorization is mandatory + logged. All commands reproducible.

**Q: Can I use this on systems I don't own?**  
A: Only with explicit written permission. Unauthorized testing is illegal.

**Q: How often should I run it?**  
A: Weekly minimum (CI/CD automation = no overhead). Quarterly+ if manual.

**Q: Does it integrate with my SIEM?**  
A: Yes. JSON findings designed for tooling. Parse + ingest as needed.

---

## Installation

### Prerequisites
- Python 3.11+
- curl, jq (usually pre-installed)
- Tools auto-installed via `--auto-install` flag

### Step 1: Clone
```bash
git clone https://github.com/ffrankito/darkscope.git
cd darkscope
```

### Step 2: Install
```bash
pip install -r requirements.txt
```

Optional: PDF support
```bash
pip install weasyprint
# macOS: brew install weasyprint
# Ubuntu: sudo apt-get install weasyprint
```

### Step 3: Verify
```bash
python3 scripts/check_tools.py --level 2
```

Auto-install if missing:
```bash
python3 scripts/check_tools.py --level 2 --auto-install
```

### Step 4: First Assessment
```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 2 --authorized --execute
```

---

## Command Reference

### Main Assessment
```bash
python3 scripts/run_assessment.py <target> \
  --level <0-5> \
  --authorized \
  --execute
```

### Supabase Testing
```bash
python3 scripts/probe_supabase.py \
  --project-ref <abc123> \
  --anon-key <eyJ...> \
  --test-cors
```

### Reports
```bash
# PDF + HTML
python3 scripts/generate_report_v2.py findings.json \
  --output-pdf report.pdf --level 5

# Dashboard
python3 scripts/dashboard.py results --output dashboard.html

# Track progress
python3 scripts/compare_baselines.py \
  --current current.json --prior prior.json
```

---

## Use Cases

🏗️ **Pre-launch review** → Level 3 assessment + PDF for stakeholder sign-off  
🔄 **Continuous monitoring** → Weekly CI/CD, auto-regression detection  
🛠️ **Fix verification** → Re-assess + baseline comparison  
📋 **Compliance audit** → PDF report with authorization log  
🔧 **Custom org checks** → Plugin system for specific requirements  

---

## License

MIT. Free to use, modify, distribute.

---

## Support

- **Detailed docs:** [IMPROVEMENTS_COMPLETED.md](IMPROVEMENTS_COMPLETED.md)
- **Example plugin:** [plugins/example_custom_checks.py](plugins/example_custom_checks.py)
- **Issues:** [GitHub Issues](https://github.com/ffrankito/darkscope/issues)

---

<div align="center">

**DarkScope: Enterprise security assessments. Safe. Repeatable. Automated.**

🕶️ [GitHub](https://github.com/ffrankito/darkscope) · 📚 [Docs](IMPROVEMENTS_COMPLETED.md) · 🐛 [Issues](https://github.com/ffrankito/darkscope/issues)

Made with ❤️ for security teams that move fast and break nothing.

</div>

