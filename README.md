<div align="center">

# 🕶️ DarkScope

### Enterprise-grade authorized pentest skill for Codex

**Recon. Evidence. Exploitability. Remediation. Retest.**

![Status](https://img.shields.io/badge/status-active-00ff88?style=for-the-badge)
![Codex Skill](https://img.shields.io/badge/codex-skill-111827?style=for-the-badge)
![AppSec](https://img.shields.io/badge/appsec-enterprise-7c3aed?style=for-the-badge)
![Safety](https://img.shields.io/badge/production-safe-blue?style=for-the-badge)

</div>

---

## ⚡ What Is DarkScope?

**DarkScope** is a Codex skill for running structured, authorized security reviews against modern web apps, SaaS platforms, CRMs, dashboards, landing pages, APIs, Supabase projects, Vercel deployments, Next.js apps, and chatbot widgets.

It is built for teams that want real offensive signal without reckless production damage.

DarkScope helps Codex choose the right depth level, run the right tools, collect clean evidence, explain findings in plain language, and produce reports that engineers can actually fix.

---

## 🧨 The DarkScope Levels

| Level | Name | Best For | Intensity |
| --- | --- | --- | --- |
| **0** | Passive Orientation | First look, unclear scope | Quiet |
| **1** | Safe Production Baseline | Low-noise production checks | Low |
| **2** | Standard Authorized Production | Real-world appsec review | Medium |
| **3** | Deep Controlled Testing | Canary-backed deeper testing | High |
| **4** | Aggressive Lab/Staging | Fake data, staging, lab attack simulation | Very High |
| **5** | Enterprise Assurance | Program-level security, CI gates, retest, tracking | Enterprise |

DarkScope separates **depth** from **destruction**.  
It can go deep without touching real customer data, brute forcing accounts, or breaking production.

---

## 🛠️ Toolchain

DarkScope works with common Kali/AppSec tools:

```text
nmap        whatweb      wafw00f      sslscan
curl        jq           katana       nikto
nuclei      feroxbuster  ffuf         ZAP
sqlmap      gitleaks     trufflehog   semgrep
trivy
```

Check your tool coverage:

```bash
./scripts/check_tools.py --level 5
```

---

## 🧬 Built For Modern Stacks

DarkScope includes focused guidance for:

- **Next.js** route/API exposure
- **Vercel** production behavior and mitigations
- **Supabase** anon keys, REST API, RLS and role policies
- **PostgREST** read/write/update/delete probes
- **JWT/session** checks
- **CORS** and security headers
- **Chatbot/API** abuse, rate limits and cost controls
- **Role-based access control** testing
- **Enterprise retesting** and remediation tracking

---

## 🚀 Quick Start

Clone or install the skill, then use it from Codex:

```text
Use $darkscope to run an authorized security review with the right depth level and a clean final report.
```

Create an assessment workspace:

```bash
./scripts/init_assessment.py my-system --level 2
```

Generate a dry-run plan:

```bash
./scripts/run_assessment.py https://example.com \
  --name example \
  --level 2 \
  --env production
```

Execute staged safe commands only when authorized:

```bash
./scripts/run_assessment.py https://example.com \
  --name example \
  --level 2 \
  --env production \
  --execute
```

Generate a sanitized report:

```bash
./scripts/generate_report.py reportes/example_YYYYMMDD_HHMMSS/resumen.md \
  --title "DarkScope Security Report"
```

---

## 🏢 Enterprise Mode

Level 5 turns DarkScope into a repeatable security program:

- Executive summary
- Technical evidence appendix
- Role matrix
- Data exposure matrix
- Remediation owner
- Due date
- Retest status
- CI security gates
- Regression checks
- Sanitized evidence package

Enterprise success criteria:

- No anonymous access to private data
- No role can read or mutate outside its business need
- Public endpoints have rate limits and abuse controls
- Findings have owners and deadlines
- Fixes are retested with evidence

---

## 🔐 Production Safety

DarkScope is designed for authorized defensive work.

In production, it avoids:

- Credential brute force
- Password spraying
- Denial-of-service
- Real data deletion
- Real data modification
- High-volume fuzzing
- High-risk SQLMap payloads
- AI/chatbot cost abuse

Instead, it proves risk with:

- HTTP status codes
- Response headers
- Counts
- Column names
- Redacted bodies
- Canary records
- Sanitized screenshots
- Reproducible commands

---

## 📁 Repository Layout

```text
darkscope/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── auth-roles.md
│   ├── enterprise.md
│   ├── levels.md
│   ├── production-safety.md
│   ├── report-template.md
│   ├── supabase-nextjs.md
│   └── tool-recipes.md
└── scripts/
    ├── check_tools.py
    ├── generate_report.py
    ├── init_assessment.py
    └── run_assessment.py
```

---

## 🧠 Example Use Cases

- Audit a production CRM without breaking it
- Validate Supabase RLS policies
- Check if anon users can read private tables
- Test role boundaries with provided test accounts
- Review Next.js/Vercel dashboards and APIs
- Scan public JS for exposed routes or secrets
- Generate a PDF report for stakeholders
- Retest fixes after remediation
- Add security checks to release workflows

---

## ⚠️ Legal

Use DarkScope only on systems you own or are explicitly authorized to test.

This project is for defensive security, hardening, validation, and responsible assessment. Do not use it for unauthorized access, credential attacks, data theft, service disruption, or destructive testing.

---

## 🕶️ Motto

> See deeper. Break nothing. Prove everything.

