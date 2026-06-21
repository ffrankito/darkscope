# 🕶️ DarkScope

> **Enterprise-grade authorized security assessments. Deep + Safe + Automated.**

[![GitHub](https://img.shields.io/badge/GitHub-ffrankito%2Fdarkscope-black?logo=github&style=for-the-badge)](https://github.com/ffrankito/darkscope)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&style=for-the-badge)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)]()
[![Free & Open Source](https://img.shields.io/badge/Free%20%26%20Open%20Source-100%25-success?style=for-the-badge)]()
[![No Paid Features](https://img.shields.io/badge/No%20Paid%20Features-0%25-success?style=for-the-badge)]()

---

## What Is DarkScope?

DarkScope is a **structured, repeatable security assessment framework** for teams that need real offensive signal without reckless production damage.

Modern apps are complex. You need to know:
- ✅ What's actually exposed to anonymous users?
- ✅ Can attackers bypass authentication?
- ✅ Are role boundaries working correctly?
- ✅ What changed since the last assessment?

**DarkScope answers these** — with safety guardrails built in, evidence automatically sanitized, and remediation tracked over time.

### The Problem It Solves

| Problem | Without DarkScope | With DarkScope |
|---------|------------------|---|
| **Tool sprawl** | Run 12+ tools, parse output manually | One command, unified report |
| **Safety** | Hope you don't break production | Conservative probes, no data writes |
| **Evidence** | Screenshots, email chains | Sanitized, reproducible, auditable |
| **Tracking** | "Did we fix that?" (unknown) | Baselines, regression detection, health scores |
| **Reporting** | Excel, Jira, Slack threads | PDF/HTML for humans, JSON for machines |
| **Repeatability** | Run-by-run variance | Automated, CI/CD-integrated, consistent |

---

## The Promise

🎯 **Go deep without breaking things**
- Aggressive probes safe for staging/lab
- Conservative read-only probes on production
- Automatic evidence sanitization (zero real customer data in reports)

🔒 **Authorization that can't be skipped**
- Explicit consent form (mandatory, no bypass flags)
- Audit log with timestamp + user + hostname
- Remediation tracking with owner + due date

📊 **Enterprise program tracking**
- Baseline comparisons (fixed vs new vs regressions)
- Health score + program trends
- Interactive dashboard with historical data

🔌 **Built for modern stacks**
- Supabase RLS testing (automated)
- Next.js/Vercel route discovery
- Rate limiting + CORS validation
- Plugin system for custom checks

---

## Quick Start

### 1. Install
```bash
git clone https://github.com/ffrankito/darkscope.git
cd darkscope
pip install -r requirements.txt
python3 scripts/check_tools.py --level 2 --auto-install
```

### 2. Authorize
```bash
python3 scripts/request_authorization.py https://your-app.com --level 2
```
→ Answer the interactive prompt. Creates audit log automatically.

### 3. Assess
```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 2 --authorized --execute --output results
```

### 4. Report
```bash
# HTML + PDF for humans
python3 scripts/generate_report_v2.py results/findings.json \
  --output-pdf report.pdf --level 5

# Dashboard with trends
python3 scripts/dashboard.py results --output dashboard.html

# Track progress
python3 scripts/compare_baselines.py \
  --current results/findings.json --prior prior/findings.json
```

Done. Open `dashboard.html` in your browser.

---

## DarkScope Levels

| Level | Name | Best For | Intensity | Data Risk |
|-------|------|----------|-----------|-----------|
| **0** | Passive Orientation | First look, unclear scope | 🟢 None | None |
| **1** | Safe Production Baseline | Low-noise production checks | 🟡 Low | Public only |
| **2** | Standard Production | Real-world appsec review (typical) | 🟠 Medium | Public + anon API |
| **3** | Deep Controlled Testing | Canary-backed deeper testing | 🔴 High | Staging + fake data |
| **4** | Aggressive Lab | Full attack simulation | 🔴🔴 Very High | Lab only |
| **5** | Enterprise Assurance | Automated program + CI gates | 🟠 Medium | Read-only production |

**Key insight:** Higher level ≠ more damage. Level 5 is actually *safer* — no destructive payloads, broad coverage, automated safely.

---

## What It Tests

### ✅ Network & Infrastructure
- Open ports, service enumeration
- TLS/SSL configuration
- Web framework detection
- Security headers (CSP, HSTS, X-Frame-Options, etc.)

### ✅ Web Application
- Route discovery (public + hidden)
- CORS misconfiguration
- Authentication/authorization flaws
- Common web vulns (low-risk probes only)
- API endpoint enumeration

### ✅ Supabase (Native Support)
- Anonymous user access to private tables
- RLS policy testing (SELECT/INSERT/UPDATE/DELETE)
- JWT claims inspection
- CORS wildcard exposure
- Per-table JSON findings

### ✅ Next.js / Vercel
- Server-side route exposure in JS bundles
- API route accessibility without auth
- Dynamic route parameter discovery
- Source map exposure

### ✅ Chatbot / API Abuse
- Rate limiting validation
- Cost control (AI endpoint throttling)
- Credentials in localStorage
- CORS + origin restrictions

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

