# DarkScope Quick Start

> Your first security assessment in 10 minutes.

## 1. Install (2 min)

```bash
git clone https://github.com/ffrankito/darkscope.git
cd darkscope
pip install -r requirements.txt
python3 scripts/check_tools.py --level 2 --auto-install
```

## 2. Run Assessment (5 min)

Choose your target:

### Level 1: Safe Production (minimal noise)
```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 1 \
  --authorized \
  --execute
```

### Level 2: Standard Production (typical)
```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 2 \
  --authorized \
  --execute
```

### Level 3: Deep Testing (staging/lab recommended)
```bash
python3 scripts/run_assessment.py https://staging.your-app.com \
  --level 3 \
  --env staging \
  --authorized \
  --execute
```

### Level 5: Enterprise (with Supabase)
```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 5 \
  --authorized \
  --execute \
  --supabase-project ABC123 \
  --supabase-key eyJ...
```

## 3. View Results (3 min)

Results are in: `./results/{domain}_{timestamp}/`

Open the dashboard:
```bash
# View latest results
open ./results/*/report.html

# Or generate dashboard
python3 scripts/dashboard.py ./results --output dashboard.html
open dashboard.html
```

---

## Full Workflow Example

### Scenario: Testing veterinary clinic CRM (NeoVet)

**Step 1: Request authorization**
```bash
python3 scripts/request_authorization.py https://neo-vet-eta.vercel.app \
  --level 2
```
→ Follow interactive prompt  
→ Creates audit log automatically

**Step 2: Run assessment**
```bash
python3 scripts/run_assessment.py https://neo-vet-eta.vercel.app \
  --level 2 \
  --authorized \
  --execute \
  --supabase-project ajpzsmcqlbbuzimjjwyi \
  --supabase-key eyJhbGc...
```

**Step 3: Sanitize evidence**
```bash
python3 scripts/sanitize_evidence.py ./results/neo-vet-eta* --aggressive
```

**Step 4: Generate PDF report**
```bash
python3 scripts/generate_report_v2.py \
  ./results/neo-vet-eta*/findings.json \
  --output-pdf ./results/neo-vet-eta*/report.pdf \
  --level 5
```

**Step 5: Create dashboard**
```bash
python3 scripts/dashboard.py ./results --output dashboard.html
open dashboard.html
```

**Step 6: Track remediation**
```bash
# After fixes are deployed, re-run:
python3 scripts/run_assessment.py https://neo-vet-eta.vercel.app \
  --level 2 \
  --authorized \
  --execute

# Compare to prior:
python3 scripts/compare_baselines.py \
  --current ./results/neo-vet-eta_20260621_120000/findings.json \
  --prior ./results/neo-vet-eta_20260620_110000/findings.json
```

---

## Dry-Run Mode (Safe for Production)

Don't want to execute tests? Use dry-run to see what would run:

```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 2 \
  --authorized
  # No --execute flag
```

Output: `run_plan.txt` with all commands that *would* run.

---

## Understanding Levels

| Level | Best For | Time | Data Risk |
|-------|----------|------|-----------|
| **0** | First look | 5 min | None |
| **1** | Production baseline | 15 min | Public only |
| **2** | Production security review (typical) | 45 min | Public + API |
| **3** | Deep testing | 2 hours | Staging only |
| **4** | Full attack simulation | 4+ hours | Lab only |
| **5** | Enterprise program tracking | 1 hour + baseline | Production-safe |

---

## Common Tasks

### Test only Supabase RLS
```bash
python3 scripts/probe_supabase.py \
  --project-ref ABC123 \
  --anon-key eyJ... \
  --test-cors \
  --output supabase_findings.json
```

### Run custom checks
```bash
python3 scripts/plugin_manager.py \
  --run https://your-app.com \
  --level 2
```

### Compare two assessments
```bash
python3 scripts/compare_baselines.py \
  --current new_findings.json \
  --prior old_findings.json
```

### Redact PII from reports
```bash
python3 scripts/sanitize_evidence.py ./results --aggressive
```

---

## Interpreting Results

### report.html / report.pdf
- **Executive Summary** (Level 5+) — stakeholder overview
- **Findings by Severity** — CRITICAL, HIGH, MEDIUM, LOW
- **Remediation Roadmap** — owner, due date, status

### findings.json
Machine-readable format for integrations:
```json
[
  {
    "title": "Supabase: patients table readable by anonymous",
    "severity": "CRITICAL",
    "table": "patients",
    "evidence": { ... },
    "recommendation": "CREATE POLICY ... FOR SELECT USING (...)"
  }
]
```

### comparison.json (if prior baseline exists)
- Fixed findings ✅
- New findings 🆕
- Regressions ⚠️
- Health trend (improving/degrading)

---

## Authorization & Logging

Every assessment creates an audit log:
```
darkscope_auth_logs/auth_20260621_113022.txt

Status:       APPROVED
Target:       https://target.com
Level:        2
User:         franco
Hostname:     mymachine
Timestamp:    2026-06-21T11:30:22
```

Use this for compliance proof.

---

## Troubleshooting

**"Authorization required but --authorized flag used"**
→ Authorization must be interactive. Remove `--authorized` flag first.

**"Missing tools for level 2"**
→ Run: `python3 scripts/check_tools.py --level 2 --auto-install`

**"No findings.json found"**
→ Make sure you used `--execute` flag. Dry-run doesn't generate findings.

**"Supabase probing failed"**
→ Check project ref and anon key. Verify Supabase project is accessible.

---

## Next Steps

- [Full README](README.md) — complete feature guide
- [IMPROVEMENTS_COMPLETED.md](IMPROVEMENTS_COMPLETED.md) — technical details
- [Create custom plugins](plugins/example_custom_checks.py) — add org-specific checks
- [Setup CI/CD](.github/workflows/darkscope.yml) — automated weekly assessments

---

**Ready to test?** Start with Level 2:

```bash
python3 scripts/run_assessment.py https://your-app.com \
  --level 2 --authorized --execute
```

Results appear in `./results/`.

Happy assessing! 🕶️
