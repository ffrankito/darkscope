# DarkScope Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   DarkScope Assessment Engine                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  run_assessment.py (Orchestrator)                           │
│  ├─ Phase 1: request_authorization.py ──→ Audit Log        │
│  ├─ Phase 2: check_tools.py ──→ Tool Verification          │
│  ├─ Phase 3: discovery & security testing                  │
│  ├─ Phase 4: probe_supabase.py ──→ RLS Testing             │
│  ├─ Phase 5: plugin_manager.py ──→ Custom Checks           │
│  ├─ Phase 6: sanitize_evidence.py ──→ PII Redaction        │
│  ├─ Phase 7: generate_report_v2.py ──→ HTML/PDF/JSON       │
│  ├─ Phase 8: compare_baselines.py ──→ Regression Detection │
│  └─ Phase 9: dashboard.py ──→ Interactive Report           │
│                                                              │
│  Storage: ./results/{domain}_{timestamp}/                  │
│  - findings.json (machine-readable)                        │
│  - report.html / report.pdf (human-readable)               │
│  - comparison.json (baseline delta)                        │
│  - assessment.log (audit trail)                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Interaction

### 1. Orchestrator (`run_assessment.py`)

Entry point for all assessments. Coordinates phases and manages state.

```python
orchestrator = AssessmentOrchestrator(
    target="https://target.com",
    level=2,
    env="production"
)
orchestrator.run(authorized=True, execute=True)
```

**Output:** Assessment directory with all results

---

### 2. Authorization (`request_authorization.py`)

Mandatory interactive prompt before testing. Cannot be skipped.

```
┌─────────────────────────────────────────────┐
│ DarkScope Authorization Confirmation        │
├─────────────────────────────────────────────┤
│ Target:  https://target.com                 │
│ Level:   2 (Standard Production)            │
│ Severity: MEDIUM - Testing, no writes       │
│                                              │
│ To proceed, type: I AUTHORIZE TESTING      │
│ > █                                        │
└─────────────────────────────────────────────┘
```

**Output:** `darkscope_auth_logs/auth_*.txt` (compliance audit log)

---

### 3. Tool Verification (`check_tools.py`)

Checks required tools are installed. Auto-installs if missing.

```
Level 0: curl, jq
Level 1: nmap, sslscan, whatweb, wafw00f
Level 2: feroxbuster, ffuf, nikto, nuclei, zap
Level 3: sqlmap, semgrep, trivy
Level 4+: Full test suite
```

**Output:** Console status (installed ✅ / missing ⚠️)

---

### 4. Discovery & Testing

Run security probes appropriate for the level.

**Level 0:** Passive fingerprinting only  
**Level 1:** Port scanning, header analysis  
**Level 2:** Route discovery, basic app testing  
**Level 3:** Data access testing  
**Level 4:** Exploitation (lab only)  
**Level 5:** Enterprise automation  

**Output:** `findings.json`

---

### 5. Supabase RLS Testing (`probe_supabase.py`)

Automated testing of Supabase projects:

```
Tests for each table:
├─ SELECT (read access)
├─ INSERT (write access)
├─ UPDATE (modify access)
├─ DELETE (delete access)
├─ CORS misconfiguration
└─ JWT claims inspection
```

**Usage:**
```bash
python3 scripts/probe_supabase.py \
  --project-ref ABC123 \
  --anon-key eyJ... \
  --test-cors
```

**Output:** Findings merged into main assessment

---

### 6. Plugin System (`plugin_manager.py`)

Extensible framework for org-specific checks.

```
plugins/
├─ example_custom_checks.py
│  ├─ NeoVetCrmPlugin
│  │  ├─ _check_patient_data_exposure()
│  │  ├─ _check_role_separation()
│  │  └─ _check_consent_protection()
│  └─ VeterinaryDataProtectionPlugin
└─ custom_plugin.py (user-created)
```

Plugin discovery:
1. Scan `./plugins/*.py`
2. Find `DarkScopePlugin` subclasses
3. Filter by level required
4. Execute and merge findings

**Output:** Plugin findings merged into main assessment

---

### 7. Evidence Sanitization (`sanitize_evidence.py`)

Removes PII before sharing reports.

Patterns redacted:
- Emails → `[EMAIL]`
- Phone numbers → `[PHONE]`
- API keys → `[API_KEY]`
- Database URLs → `[DATABASE_URL]`
- JWTs → `[JWT]`
- Credit cards → `[CREDIT_CARD]`

**Usage:**
```bash
python3 scripts/sanitize_evidence.py ./results --aggressive
```

**Output:** Sanitized findings safe for non-security staff

---

### 8. Report Generation (`generate_report_v2.py`)

Generates human and machine-readable reports.

#### HTML Report
```
┌─────────────────────────────────────┐
│ Executive Summary (Level 5+)        │
│ ├─ Critical: 1                      │
│ ├─ High: 3                          │
│ ├─ Health Score: 65%                │
│ └─ Recommendations                  │
├─────────────────────────────────────┤
│ Findings by Severity                │
│ ├─ CRITICAL (1)                     │
│ ├─ HIGH (3)                         │
│ └─ MEDIUM (2)                       │
├─────────────────────────────────────┤
│ Remediation Roadmap (Level 5+)      │
│ ├─ Owner: Franco (4 findings)       │
│ ├─ Owner: Security Team (2)         │
│ └─ Due dates + status               │
└─────────────────────────────────────┘
```

#### JSON Findings
```json
{
  "findings": [
    {
      "title": "RLS policy missing",
      "severity": "CRITICAL",
      "table": "patients",
      "evidence": { ... },
      "recommendation": "CREATE POLICY ... FOR SELECT"
    }
  ]
}
```

**Output:** `report.html`, `report.pdf` (L5+), `findings.json`

---

### 9. Baseline Comparison (`compare_baselines.py`)

Tracks progress between assessments.

```
Comparison Report
═══════════════════════════════════
Fixed:        5 ✅
New:          2 🆕
Regressions:  0 ⚠️
Improvements: 3 📈

Critical Count:
  Prior:     3
  Current:   1
  Delta:    -2 ✅

Health Trend: IMPROVING 📈
```

**Output:** `comparison.json`

---

### 10. Dashboard (`dashboard.py`)

Interactive HTML dashboard with Chart.js trends.

```
Metrics:
├─ Current Critical: 1
├─ Current High: 3
├─ Assessment Count: 5
└─ Health Score: 65%

Trends:
├─ Critical Over Time (line chart)
├─ High Over Time (line chart)
├─ Distribution (doughnut chart)
└─ Assessment History (table)
```

**Usage:**
```bash
python3 scripts/dashboard.py ./results --output dashboard.html
```

**Output:** `dashboard.html` (open in browser)

---

## Data Flow

```
User Input
    ↓
request_authorization.py
    ↓ (user confirms)
check_tools.py
    ↓ (tools verified)
Discovery & Testing (main phase)
    ├─→ run_assessment.py (orchestrator)
    ├─→ probe_supabase.py (RLS testing)
    └─→ plugin_manager.py (custom checks)
    ↓
findings.json (raw results)
    ↓
sanitize_evidence.py
    ↓
findings.json (sanitized)
    ↓
generate_report_v2.py
    ├─→ report.html
    ├─→ report.pdf (L5+)
    └─→ findings.json
    ↓
compare_baselines.py (optional)
    ↓
comparison.json
    ↓
dashboard.py
    ↓
dashboard.html
    ↓
View Results
```

---

## Configuration

Central config: `.darkscope.yml`

```yaml
default_level: 2
default_env: production

phases_by_level:
  0: [basic_recon]
  1: [basic_recon, content_discovery]
  2: [basic_recon, content_discovery, app_testing, vulnerability_scanning]
  # ... etc
```

Command-line overrides config file:
```bash
# Uses .darkscope.yml default (level 2)
python3 scripts/run_assessment.py https://target.com

# Override to level 3
python3 scripts/run_assessment.py https://target.com --level 3
```

---

## Storage Structure

```
results/
├─ neo-vet-eta_20260621_120000/  ← Assessment ID
│  ├─ findings.json              ← Raw findings
│  ├─ report.html                ← HTML report
│  ├─ report.pdf                 ← PDF report (L5+)
│  ├─ comparison.json            ← Baseline delta
│  ├─ assessment.log             ← Detailed audit
│  └─ darkscope_auth_logs/       ← Authorization proof
│     └─ auth_20260621_120000.txt
├─ neo-vet-eta_20260620_110000/
│  └─ (previous assessment)
└─ ...
```

---

## Security Boundaries

### Authorization (Mandatory)
- Cannot be skipped
- Interactive prompt required
- Logged to compliance audit file

### Evidence Sanitization (Automatic)
- All findings sanitized before reporting
- PII patterns redacted
- Safe for sharing with non-security staff

### Tool Safety
- Level 4 forbidden on production
- No credential attacks
- No DOS attacks
- Destruction prevented

---

## Integration Points

### GitHub Actions (CI/CD)
```yaml
# .github/workflows/darkscope.yml
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  assessment:
    runs-on: ubuntu-latest
    steps:
      - run: python3 scripts/run_assessment.py ... --execute
      - run: python3 scripts/compare_baselines.py ... --fail-on-regression
      - run: python3 scripts/dashboard.py ... (generate)
      - uses: actions/upload-artifact@v4
        with:
          name: darkscope-results
```

### Slack Notifications
```python
# .github/workflows/darkscope.yml
- if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      { "text": "🚨 DarkScope found critical findings" }
```

### SIEM Integration
```bash
# Export findings as JSON for tooling
cat ./results/*/findings.json | jq '.' | \
  curl -X POST https://siem.internal/ingest \
    -H "Content-Type: application/json" \
    -d @-
```

---

## Performance

### Typical Timing

| Level | Time | Notes |
|-------|------|-------|
| 0 | 5 min | Passive only |
| 1 | 15 min | Network recon |
| 2 | 45 min | Application testing |
| 3 | 2 hours | Deep data testing |
| 4 | 4+ hours | Exploitation |
| 5 | 1 hour | Enterprise (production-safe) |

### Parallelization

- Phases run sequentially (auth → tools → testing → reporting)
- Within testing, probes can run in parallel (10 concurrent max for production)
- Report generation is single-threaded (minimal overhead)

---

## Future Enhancements

- [ ] Real-time progress streaming
- [ ] Custom test templates
- [ ] Machine learning anomaly detection
- [ ] Automated remediation suggestions
- [ ] Multi-target batch assessments
- [ ] Integration with threat intelligence feeds

---

**DarkScope is architected for safety, repeatability, and enterprise automation.** Every phase is logged, evidence is sanitized, and authorization is mandatory.
