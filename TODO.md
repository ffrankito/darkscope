# DarkScope TODO — Complete Feature Roadmap

> What's done. What's in progress. What's not done.

---

## ✅ DONE (v2.0 - Current)

### Core Infrastructure
- [x] Orchestrator (`run_assessment.py`) coordinating all phases
- [x] Authorization system (mandatory, audit-logged)
- [x] Tool detection & auto-install (`check_tools.py`)
- [x] Evidence sanitization (`sanitize_evidence.py`)
- [x] Report generation (`generate_report_v2.py`) — HTML/JSON
- [x] Baseline tracking (`compare_baselines.py`)
- [x] Dashboard (`dashboard.py`) — Chart.js trends
- [x] Configuration system (`.darkscope.yml`)
- [x] Plugin system (`plugin_manager.py`)

### Tool Integrators (Real Security Testing)
- [x] Reconnaissance (`reconnaissance.py`)
  - [x] HTTP headers validation
  - [x] Technology fingerprinting (whatweb)
  - [x] WAF detection (wafw00f)
  - [x] Network scanning (nmap)
  - [x] SSL/TLS analysis (sslscan)
- [x] Discovery (`discovery.py`)
  - [x] Manual route testing
  - [x] Directory fuzzing (ffuf, feroxbuster)
  - [x] JavaScript analysis
  - [x] Full crawl (katana)
- [x] Vulnerability Scanning (`vulnerability_scanning.py`)
  - [x] nikto integration
  - [x] nuclei integration
  - [x] zap integration
- [x] SQL Testing (`sql_testing.py`)
  - [x] Manual SQLi testing
  - [x] sqlmap integration
- [x] Code Analysis (`code_analysis.py`)
  - [x] semgrep (SAST)
  - [x] npm audit
  - [x] pip audit
  - [x] trivy (CVE scanning)
- [x] Supabase RLS Testing (`probe_supabase.py`)

### Documentation
- [x] Professional README (security-focused)
- [x] QUICKSTART (first assessment in 10 min)
- [x] ARCHITECTURE (complete system design)
- [x] IMPROVEMENTS_COMPLETED (technical reference)

### Security & Compliance
- [x] HTML injection fixes
- [x] Credential exposure fixes
- [x] SSL verification enforcement
- [x] Authorization audit logging
- [x] PII sanitization (emails, phones, DNI, JWT, API keys, DB URLs)

---

## 🚧 IN PROGRESS (v2.1 - Next)

- [ ] PDF generation (weasyprint integration) — partially done
- [ ] Real tool execution (currently mocked in some phases)
- [ ] Comprehensive test coverage
- [ ] Cross-platform CI/CD testing

---

## ❌ NOT DONE (Backlog)

### Phase Completions
- [ ] **Reconnaissance.py** — Actual tool output parsing needs refinement
  - [ ] whatweb output parsing (more patterns)
  - [ ] nmap XML parsing (instead of text)
  - [ ] sslscan detailed parsing
  - [ ] HSTS preload checking
  - [ ] DNSSEC validation

- [ ] **Discovery.py** — Routes need filtering & validation
  - [ ] Duplicate route elimination
  - [ ] 404 false positive filtering
  - [ ] Parameter type detection (int, uuid, slug)
  - [ ] Endpoint documentation generation
  - [ ] GraphQL endpoint detection

- [ ] **Vulnerability_scanning.py** — Better severity mapping
  - [ ] CVSS scoring integration
  - [ ] CWE mapping
  - [ ] OWASP Top 10 categorization
  - [ ] Real ZAP output parsing (currently simplified)

- [ ] **SQL_testing.py** — More sophisticated detection
  - [ ] Time-based SQLi
  - [ ] Blind SQLi (boolean-based)
  - [ ] Union-based SQLi
  - [ ] ORM-specific patterns
  - [ ] NoSQL injection testing

- [ ] **Code_analysis.py** — Expanded coverage
  - [ ] Go/Rust dependency scanning
  - [ ] Java/Maven analysis
  - [ ] Docker image scanning
  - [ ] License compliance checking
  - [ ] SBOM generation

### New Testing Phases (Not Integrated)
- [ ] **Authentication Testing**
  - [ ] Credential stuffing detection
  - [ ] Session fixation
  - [ ] Two-factor bypass attempts (safe)
  - [ ] Token expiration validation
  - [ ] CSRF testing

- [ ] **Authorization Testing**
  - [ ] Role-based access control (RBAC) testing
  - [ ] Attribute-based access control (ABAC) testing
  - [ ] Horizontal privilege escalation
  - [ ] Vertical privilege escalation
  - [ ] Data-based authorization bypass

- [ ] **Cryptography Testing**
  - [ ] Weak encryption detection
  - [ ] Key storage validation
  - [ ] Random number generator testing
  - [ ] Hashing algorithm analysis

- [ ] **Business Logic Testing**
  - [ ] Workflow bypass detection
  - [ ] Price manipulation
  - [ ] Concurrency issues
  - [ ] Race conditions

- [ ] **Mobile/API Specific**
  - [ ] API rate limiting validation
  - [ ] API versioning issues
  - [ ] Mobile certificate pinning
  - [ ] Jailbreak/Root detection bypass

### Reporting & Tracking
- [ ] PDF generation working (not just scaffolded)
- [ ] Executive summary (L5+) refinement
- [ ] Remediation roadmap improvements
- [ ] Metrics dashboard enhancements
- [ ] Real-time progress streaming
- [ ] WebSocket integration for live updates

### Integration & Automation
- [ ] GitHub Actions workflow testing
- [ ] Slack integration (real notifications)
- [ ] JIRA ticket creation
- [ ] Linear API integration
- [ ] Email report distribution
- [ ] Webhook POST of findings

### Data & Analytics
- [ ] Historical trend analysis (more than just comparison)
- [ ] Predictive vulnerability scoring
- [ ] Machine learning for false positive elimination
- [ ] Remediation time tracking
- [ ] Time-to-fix metrics

### Safety & Compliance
- [ ] Rate limiting for aggressive phases
- [ ] Concurrency limits (parallel probe execution)
- [ ] Rollback capabilities
- [ ] Dry-run validation
- [ ] Pre-execution safety checks
- [ ] Compliance templates (HIPAA, PCI-DSS, GDPR)

### DevOps & Scaling
- [ ] Docker container support
- [ ] Kubernetes job integration
- [ ] Distributed assessment (multiple targets in parallel)
- [ ] Cloud provider detection (AWS, GCP, Azure)
- [ ] Database clustering detection

### Community & Extensibility
- [ ] Plugin marketplace
- [ ] Custom rule builder UI
- [ ] Assessment template library
- [ ] Community findings database
- [ ] Integration with threat intelligence

### Performance & Optimization
- [ ] Caching for repeated targets
- [ ] Incremental assessment (only test changed endpoints)
- [ ] Parallel probe execution with concurrency limits
- [ ] Progressive reporting (stream findings as they come in)
- [ ] Memory optimization for large response sets

### Testing & QA
- [ ] Unit test coverage (>80%)
- [ ] Integration test suite
- [ ] Real tool testing (not mocks)
- [ ] End-to-end workflow testing
- [ ] Cross-platform compatibility (Linux, macOS, Windows)
- [ ] Python 3.11+ version validation

---

## 🎯 Priority Breakdown

### CRITICAL (Needed for v2.0 Release)
- [ ] PDF generation actually working
- [ ] Real tool output parsing (not mocks)
- [ ] End-to-end workflow testing

### HIGH (v2.1)
- [ ] Authentication testing phase
- [ ] Authorization testing phase
- [ ] Slack/GitHub integration
- [ ] Comprehensive test coverage

### MEDIUM (v2.2)
- [ ] Business logic testing
- [ ] Mobile/API specific testing
- [ ] ML false positive filtering
- [ ] Docker/Kubernetes support

### LOW (v3.0)
- [ ] Plugin marketplace
- [ ] Predictive scoring
- [ ] Distributed assessment
- [ ] Community features

---

## 📊 Completion Status

```
Core Framework:     ████████████░░░░░░░░ 65%
Tool Integrators:   ██████████░░░░░░░░░░ 50%
Testing Phases:     ███████░░░░░░░░░░░░░ 35%
Automation:         ████░░░░░░░░░░░░░░░░ 20%
Enterprise Features:████░░░░░░░░░░░░░░░░ 20%
Documentation:      ██████████░░░░░░░░░░ 50%
Security:           ████████████░░░░░░░░ 60%

OVERALL:            ███████░░░░░░░░░░░░░ 45%
```

---

## 🔧 Tech Debt

- [ ] Refactor report generation (too many methods)
- [ ] Consolidate tool parsing logic (similar patterns)
- [ ] Improve error handling (currently basic)
- [ ] Add type hints everywhere (partial coverage)
- [ ] Remove debug print statements
- [ ] Standardize finding schema (inconsistent fields)

---

## 🐛 Known Issues

- [ ] Feroxbuster parsing fails on some output formats
- [ ] Nuclei JSON parsing incomplete (handles only subset)
- [ ] ZAP integration is basic (not real active scan)
- [ ] PDF generation requires weasyprint (heavy dependency)
- [ ] Dashboard Chart.js CDN might be blocked in restricted networks
- [ ] Authorization prompt doesn't handle piped input (TTY only)

---

## 🚀 Next Steps (If You Want To Help)

1. **Test real tools** — Run against staging environment, validate outputs
2. **Implement PDF** — Get weasyprint PDF generation working properly
3. **Add auth testing** — Most security frameworks skip this
4. **CI/CD integration** — Make .github/workflows/darkscope.yml work
5. **Community plugins** — Build example plugins for different frameworks

---

## 📝 Notes

- All percentages are rough estimates
- Tool integrations are functional but output parsing could be deeper
- Many integrations are "happy path" only (minimal error handling)
- Production use requires real testing with actual tools
- This is actively developed; priorities may shift

Last updated: 2026-06-21
