#!/usr/bin/env python3
"""
Generate DarkScope security reports with Executive Summary, PDF export, and baseline comparison.
Supports Levels 0-5 with enterprise-grade reporting for Level 5.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

class ReportGenerator:
    """Generate comprehensive security assessment reports"""

    SEVERITY_COLORS = {
        'CRITICAL': '#dc3545',
        'HIGH': '#fd7e14',
        'MEDIUM': '#ffc107',
        'LOW': '#17a2b8',
        'INFO': '#6c757d',
    }

    SEVERITY_ORDER = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}

    def __init__(self, findings: List[Dict], level: int = 2, prior_baseline: Optional[Dict] = None):
        self.findings = findings
        self.level = level
        self.prior_baseline = prior_baseline
        self.timestamp = datetime.now().isoformat()

    def render_executive_summary(self) -> str:
        """Executive summary (Level 5 feature)"""
        critical = len([f for f in self.findings if f.get('severity') == 'CRITICAL'])
        high = len([f for f in self.findings if f.get('severity') == 'HIGH'])
        medium = len([f for f in self.findings if f.get('severity') == 'MEDIUM'])

        delta = self._compute_delta()

        html = f"""
        <section class="executive-summary">
            <h2>Executive Summary</h2>

            <div class="metrics-grid">
                <div class="metric critical">
                    <div class="number">{critical}</div>
                    <div class="label">Critical</div>
                </div>
                <div class="metric high">
                    <div class="number">{high}</div>
                    <div class="label">High</div>
                </div>
                <div class="metric medium">
                    <div class="number">{medium}</div>
                    <div class="label">Medium</div>
                </div>
                <div class="metric status">
                    <div class="number">{self._health_score()}%</div>
                    <div class="label">Program Health</div>
                </div>
            </div>

            <h3>Assessment Date</h3>
            <p>{self.timestamp}</p>

            <h3>Prior Assessment Comparison</h3>
            {self._render_delta_summary(delta)}

            <h3>Recommendation</h3>
            {self._render_recommendation()}
        </section>
        """
        return html

    def render_findings_by_severity(self) -> str:
        """Render findings grouped by severity"""
        by_severity = defaultdict(list)
        for finding in self.findings:
            severity = finding.get('severity', 'INFO')
            by_severity[severity].append(finding)

        html = '<section class="findings"><h2>Findings</h2>'

        for severity in sorted(self.SEVERITY_ORDER.keys(), key=lambda x: self.SEVERITY_ORDER[x]):
            if severity not in by_severity:
                continue

            findings = by_severity[severity]
            color = self.SEVERITY_COLORS[severity]

            html += f"""
            <h3 style="color: {color}">● {severity} ({len(findings)})</h3>
            <table class="findings-table">
                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Finding</th>
                        <th>Owner</th>
                        <th>Due Date</th>
                    </tr>
                </thead>
                <tbody>
            """

            for finding in findings:
                owner = finding.get('owner', 'UNASSIGNED')
                due_date = finding.get('due_date', 'TBD')
                asset = finding.get('table', 'N/A')
                title = finding.get('title', finding.get('operation', 'Unknown'))

                html += f"""
                <tr>
                    <td>{asset}</td>
                    <td>{title}</td>
                    <td>{owner}</td>
                    <td>{due_date}</td>
                </tr>
                """

            html += """
                </tbody>
            </table>
            """

        html += '</section>'
        return html

    def render_remediation_roadmap(self) -> str:
        """Remediation roadmap (Level 5 feature)"""
        by_owner = defaultdict(list)
        for finding in self.findings:
            owner = finding.get('owner', 'UNASSIGNED')
            by_owner[owner].append(finding)

        html = '<section class="remediation"><h2>Remediation Roadmap</h2>'

        for owner in sorted(by_owner.keys()):
            findings = by_owner[owner]
            critical_count = len([f for f in findings if f.get('severity') == 'CRITICAL'])

            html += f"""
            <h3>Owned by: {owner} ({len(findings)} findings, {critical_count} critical)</h3>
            <ul>
            """

            for finding in findings:
                html += f"""
                <li>
                    <strong>{finding.get('title', 'Unknown')}</strong>
                    <br/>Severity: {finding.get('severity', 'INFO')}
                    <br/>Due: {finding.get('due_date', 'TBD')}
                    <br/>Recommendation: {finding.get('recommendation', 'N/A')}
                </li>
                """

            html += '</ul>'

        html += '</section>'
        return html

    def _compute_delta(self) -> Dict:
        """Compare current findings to prior baseline"""
        if not self.prior_baseline:
            return {'fixed': [], 'regressions': [], 'new': []}

        prior_findings = {(f.get('table'), f.get('operation')): f for f in self.prior_baseline.get('findings', [])}
        current_findings = {(f.get('table'), f.get('operation')): f for f in self.findings}

        fixed = [f for key, f in prior_findings.items() if key not in current_findings]
        new = [f for key, f in current_findings.items() if key not in prior_findings]
        regressions = []  # Findings that got worse

        return {
            'fixed': fixed,
            'new': new,
            'regressions': regressions
        }

    def _render_delta_summary(self, delta: Dict) -> str:
        """Render delta comparison"""
        if not self.prior_baseline:
            return "<p>No prior assessment available for comparison.</p>"

        fixed = len(delta['fixed'])
        new = len(delta['new'])
        regressions = len(delta['regressions'])

        html = f"""
        <ul>
            <li>✅ <strong>{fixed}</strong> findings fixed</li>
            <li>🆕 <strong>{new}</strong> new findings</li>
            <li>⚠️ <strong>{regressions}</strong> regressions</li>
        </ul>
        """

        if regressions > 0:
            html += '<p style="color: red;"><strong>⚠️ REGRESSIONS DETECTED: Review recently fixed findings.</strong></p>'

        return html

    def _render_recommendation(self) -> str:
        """Render security recommendation"""
        critical = len([f for f in self.findings if f.get('severity') == 'CRITICAL'])

        if critical > 0:
            return f"""
            <p style="color: red;">
                <strong>🚨 CRITICAL: This system has {critical} critical security findings.</strong>
                <br/>
                Immediate remediation required before production deployment.
                Estimated timeline: 7-14 days.
            </p>
            """
        else:
            return """
            <p style="color: green;">
                <strong>✅ No critical findings.</strong>
                <br/>
                Proceed with remediation plan for high/medium severity items.
            </p>
            """

    def _health_score(self) -> int:
        """Calculate program health percentage (0-100)"""
        if not self.findings:
            return 100

        severity_weights = {'CRITICAL': 20, 'HIGH': 10, 'MEDIUM': 5, 'LOW': 1, 'INFO': 0}
        total_weight = sum(severity_weights.get(f.get('severity'), 0) for f in self.findings)

        # Max score of 100
        score = max(0, 100 - total_weight)
        return score

    def render_html(self) -> str:
        """Render complete HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>DarkScope Security Assessment Report</title>
            <style>
                {self._render_css()}
            </style>
        </head>
        <body>
            <header class="report-header">
                <h1>🕶️ DarkScope Security Assessment Report</h1>
                <p class="meta">Generated: {self.timestamp}</p>
                <p class="meta">Assessment Level: {self.level}/5</p>
            </header>

            {self.render_executive_summary() if self.level >= 5 else ''}
            {self.render_findings_by_severity()}
            {self.render_remediation_roadmap() if self.level >= 5 else ''}

            <footer class="report-footer">
                <p>This report contains sensitive security information.</p>
                <p>Distribute only to authorized personnel.</p>
            </footer>
        </body>
        </html>
        """
        return html

    @staticmethod
    def _render_css() -> str:
        return """
        * { margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; padding: 20px; }
        .report-header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .report-header h1 { color: #0f172a; margin-bottom: 10px; }
        .meta { color: #666; font-size: 12px; }
        section { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
        h2 { color: #0f172a; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 15px; }
        h3 { color: #333; margin-top: 15px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .metric { padding: 15px; border-radius: 8px; text-align: center; color: white; }
        .metric.critical { background: #dc3545; }
        .metric.high { background: #fd7e14; }
        .metric.medium { background: #ffc107; color: #333; }
        .metric.status { background: #17a2b8; }
        .metric .number { font-size: 28px; font-weight: bold; }
        .metric .label { font-size: 12px; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f0f0f0; font-weight: bold; }
        ul { margin-left: 20px; }
        li { margin: 8px 0; }
        .report-footer { text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 20px; margin-top: 40px; }
        """

    def save_html(self, output_file: Path) -> Path:
        """Save report as HTML"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.render_html())
        return output_file

    def save_pdf(self, output_file: Path) -> Optional[Path]:
        """Save report as PDF (requires weasyprint)"""
        try:
            from weasyprint import HTML
        except ImportError:
            print("⚠️  weasyprint not installed. Skipping PDF generation.")
            print("   Install with: pip install weasyprint")
            return None

        html_content = self.render_html()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            HTML(string=html_content).write_pdf(output_file)
            return output_file
        except Exception as e:
            print(f"❌ Failed to generate PDF: {e}")
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate DarkScope security reports.")
    parser.add_argument("input", help="Input findings JSON file")
    parser.add_argument("--output-html", help="Output HTML file")
    parser.add_argument("--output-pdf", help="Output PDF file")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2, help="Assessment level (0-5)")
    parser.add_argument("--prior-baseline", help="Prior baseline JSON for comparison")
    args = parser.parse_args()

    # Load findings
    with open(args.input) as f:
        findings = json.load(f)

    # Load prior baseline if provided
    prior_baseline = None
    if args.prior_baseline:
        with open(args.prior_baseline) as f:
            prior_baseline = json.load(f)

    # Generate report
    generator = ReportGenerator(findings, level=args.level, prior_baseline=prior_baseline)

    # Save HTML
    html_file = args.output_html or Path(args.input).with_suffix('.html')
    generator.save_html(Path(html_file))
    print(f"✅ HTML report saved: {html_file}")

    # Save PDF
    if args.output_pdf:
        pdf_file = generator.save_pdf(Path(args.output_pdf))
        if pdf_file:
            print(f"✅ PDF report saved: {pdf_file}")


if __name__ == "__main__":
    main()
