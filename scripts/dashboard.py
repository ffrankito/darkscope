#!/usr/bin/env python3
"""
DarkScope Security Program Dashboard.
Tracks assessment history, trends, and program health over time.
"""

import json
import sys
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

class Dashboard:
    """Generate interactive security program dashboard"""

    def __init__(self, assessments_dir: Path):
        self.assessments_dir = assessments_dir
        self.assessments = self._load_assessments()

    def _load_assessments(self) -> List[Dict]:
        """Load all assessment reports"""
        assessments = []

        for report_file in sorted(self.assessments_dir.glob('**/findings.json')):
            try:
                with open(report_file) as f:
                    data = json.load(f)

                assessment = {
                    'file': str(report_file),
                    'date': report_file.parent.name,
                    'findings': data if isinstance(data, list) else data.get('findings', [])
                }

                assessments.append(assessment)
            except:
                pass

        return sorted(assessments, key=lambda a: a['date'])

    def generate_metrics(self) -> Dict:
        """Generate aggregated metrics"""
        if not self.assessments:
            return {}

        latest = self.assessments[-1]
        findings = latest['findings']

        severity_counts = defaultdict(int)
        for finding in findings:
            severity = finding.get('severity', 'INFO')
            severity_counts[severity] += 1

        return {
            'total_assessments': len(self.assessments),
            'latest_date': latest['date'],
            'latest_findings': len(findings),
            'critical': severity_counts['CRITICAL'],
            'high': severity_counts['HIGH'],
            'medium': severity_counts['MEDIUM'],
            'low': severity_counts['LOW'],
        }

    def generate_trends(self) -> Dict:
        """Generate finding trends over time"""
        trends = {
            'critical': [],
            'high': [],
            'medium': [],
            'total': []
        }

        for assessment in self.assessments:
            findings = assessment['findings']
            severity_counts = defaultdict(int)

            for finding in findings:
                severity = finding.get('severity', 'INFO')
                severity_counts[severity] += 1

            trends['critical'].append({
                'date': assessment['date'],
                'count': severity_counts['CRITICAL']
            })
            trends['high'].append({
                'date': assessment['date'],
                'count': severity_counts['HIGH']
            })
            trends['medium'].append({
                'date': assessment['date'],
                'count': severity_counts['MEDIUM']
            })
            trends['total'].append({
                'date': assessment['date'],
                'count': len(findings)
            })

        return trends

    def render_html(self) -> str:
        """Render interactive HTML dashboard"""
        metrics = self.generate_metrics()
        trends = self.generate_trends()

        if not metrics:
            return "<p>No assessments found.</p>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>DarkScope Security Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js" integrity="sha384-eNQQN0F1EiziY3eU3BnN/lW4jQJvXx8FUJFPFNhvwdMH0XKHLPuSW3bw+EIeL7Ag5K" crossorigin="anonymous"></script>
            <style>
                {self._render_css()}
            </style>
        </head>
        <body>
            <header class="dashboard-header">
                <h1>🕶️ DarkScope Security Dashboard</h1>
                <p class="meta">Last updated: {metrics['latest_date']}</p>
            </header>

            <div class="container">
                <section class="metrics-section">
                    <h2>Current Status</h2>
                    <div class="metrics-grid">
                        <div class="metric critical">
                            <div class="number">{metrics['critical']}</div>
                            <div class="label">Critical</div>
                        </div>
                        <div class="metric high">
                            <div class="number">{metrics['high']}</div>
                            <div class="label">High</div>
                        </div>
                        <div class="metric medium">
                            <div class="number">{metrics['medium']}</div>
                            <div class="label">Medium</div>
                        </div>
                        <div class="metric low">
                            <div class="number">{metrics['low']}</div>
                            <div class="label">Low</div>
                        </div>
                        <div class="metric info">
                            <div class="number">{metrics['total_assessments']}</div>
                            <div class="label">Assessments</div>
                        </div>
                        <div class="metric health">
                            <div class="number">{self._calculate_health_score(metrics)}%</div>
                            <div class="label">Health Score</div>
                        </div>
                    </div>
                </section>

                <section class="chart-section">
                    <h2>Finding Trends</h2>
                    <canvas id="trendsChart"></canvas>
                </section>

                <section class="chart-section">
                    <h2>Current Distribution</h2>
                    <div style="width: 50%; margin: 0 auto;">
                        <canvas id="distributionChart"></canvas>
                    </div>
                </section>

                <section class="assessment-history">
                    <h2>Assessment History</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Critical</th>
                                <th>High</th>
                                <th>Medium</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._render_history_table(trends)}
                        </tbody>
                    </table>
                </section>
            </div>

            <script>
                {self._render_javascript(trends, metrics)}
            </script>
        </body>
        </html>
        """

        return html

    def _render_history_table(self, trends: Dict) -> str:
        """Render assessment history table"""
        rows = ""
        for i, date_entry in enumerate(trends['total']):
            date = html.escape(str(date_entry['date']))
            critical = html.escape(str(trends['critical'][i]['count']))
            high = html.escape(str(trends['high'][i]['count']))
            medium = html.escape(str(trends['medium'][i]['count']))
            total = html.escape(str(date_entry['count']))

            rows += f"""
            <tr>
                <td>{date}</td>
                <td style="color: #dc3545;">{critical}</td>
                <td style="color: #fd7e14;">{high}</td>
                <td style="color: #ffc107; color: #333;">{medium}</td>
                <td><strong>{total}</strong></td>
            </tr>
            """

        return rows

    def _render_javascript(self, trends: Dict, metrics: Dict) -> str:
        """Render Chart.js initialization"""
        dates = [t['date'] for t in trends['total']]
        critical_data = [t['count'] for t in trends['critical']]
        high_data = [t['count'] for t in trends['high']]
        medium_data = [t['count'] for t in trends['medium']]

        js = f"""
        // Trends chart
        const trendsCtx = document.getElementById('trendsChart').getContext('2d');
        new Chart(trendsCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [
                    {{
                        label: 'Critical',
                        data: {critical_data},
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'High',
                        data: {high_data},
                        borderColor: '#fd7e14',
                        backgroundColor: 'rgba(253, 126, 20, 0.1)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Medium',
                        data: {medium_data},
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: true, position: 'top' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // Distribution chart
        const distCtx = document.getElementById('distributionChart').getContext('2d');
        new Chart(distCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{{
                    data: [{metrics['critical']}, {metrics['high']}, {metrics['medium']}, {metrics['low']}],
                    backgroundColor: [
                        '#dc3545',
                        '#fd7e14',
                        '#ffc107',
                        '#17a2b8'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        """

        return js

    @staticmethod
    def _render_css() -> str:
        return """
        * { margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }
        .dashboard-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .dashboard-header h1 { font-size: 36px; margin-bottom: 10px; }
        .meta { opacity: 0.9; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        section { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
        .metric { padding: 20px; border-radius: 8px; color: white; text-align: center; }
        .metric.critical { background: #dc3545; }
        .metric.high { background: #fd7e14; }
        .metric.medium { background: #ffc107; color: #333; }
        .metric.low { background: #17a2b8; }
        .metric.info { background: #6c757d; }
        .metric.health { background: #28a745; }
        .metric .number { font-size: 32px; font-weight: bold; }
        .metric .label { font-size: 12px; margin-top: 5px; opacity: 0.9; }
        .chart-section { position: relative; height: 400px; }
        .assessment-history { }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f0f0f0; font-weight: bold; }
        tr:hover { background: #f9f9f9; }
        """

    @staticmethod
    def _calculate_health_score(metrics: Dict) -> int:
        """Calculate overall health score (0-100)"""
        if metrics['critical'] == 0 and metrics['high'] == 0:
            return 100
        elif metrics['critical'] == 0:
            return max(0, 100 - (metrics['high'] * 5))
        else:
            return max(0, 100 - (metrics['critical'] * 20) - (metrics['high'] * 5))

    def save_html(self, output_file: Path) -> Path:
        """Save dashboard as HTML"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.render_html())
        return output_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate DarkScope security dashboard.")
    parser.add_argument("assessments_dir", help="Directory containing assessment reports")
    parser.add_argument("--output", help="Output HTML file (default: dashboard.html)")
    args = parser.parse_args()

    assessments_dir = Path(args.assessments_dir)
    if not assessments_dir.exists():
        print(f"❌ Directory not found: {assessments_dir}")
        sys.exit(1)

    dashboard = Dashboard(assessments_dir)
    output_file = args.output or "dashboard.html"

    dashboard.save_html(Path(output_file))
    print(f"✅ Dashboard generated: {output_file}")
    print(f"   Open in browser: file://{Path(output_file).absolute()}")


if __name__ == "__main__":
    main()
