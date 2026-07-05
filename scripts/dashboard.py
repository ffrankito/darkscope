#!/usr/bin/env python3
"""
DarkScope Security Program Dashboard.
Tracks assessment history, trends, and program health over time.
"""

import json
import sys
import html as html_lib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class Dashboard:
    """Generate interactive security program dashboard"""

    SEVERITY_COLORS = {
        'CRITICAL': '#ef4444',
        'HIGH':     '#f97316',
        'MEDIUM':   '#eab308',
        'LOW':      '#22d3ee',
        'INFO':     '#64748b',
    }

    def __init__(self, assessments_dir: Path):
        self.assessments_dir = assessments_dir
        self.assessments = self._load_assessments()

    def _load_assessments(self) -> List[Dict]:
        assessments = []
        for report_file in sorted(self.assessments_dir.glob('**/findings.json')):
            try:
                with open(report_file) as f:
                    data = json.load(f)
                assessments.append({
                    'file': str(report_file),
                    'date': report_file.parent.name,
                    'findings': data if isinstance(data, list) else data.get('findings', [])
                })
            except Exception:
                pass
        return sorted(assessments, key=lambda a: a['date'])

    def generate_metrics(self) -> Dict:
        if not self.assessments:
            return {}
        latest = self.assessments[-1]
        findings = latest['findings']
        counts = defaultdict(int)
        for f in findings:
            counts[f.get('severity', 'INFO')] += 1
        return {
            'total_assessments': len(self.assessments),
            'latest_date': latest['date'],
            'latest_findings': len(findings),
            'critical': counts['CRITICAL'],
            'high': counts['HIGH'],
            'medium': counts['MEDIUM'],
            'low': counts['LOW'],
            'info': counts['INFO'],
        }

    def generate_trends(self) -> Dict:
        trends = {'critical': [], 'high': [], 'medium': [], 'total': []}
        for a in self.assessments:
            counts = defaultdict(int)
            for f in a['findings']:
                counts[f.get('severity', 'INFO')] += 1
            trends['critical'].append({'date': a['date'], 'count': counts['CRITICAL']})
            trends['high'].append({'date': a['date'], 'count': counts['HIGH']})
            trends['medium'].append({'date': a['date'], 'count': counts['MEDIUM']})
            trends['total'].append({'date': a['date'], 'count': len(a['findings'])})
        return trends

    @staticmethod
    def _health_score(metrics: Dict) -> int:
        c = metrics.get('critical', 0)
        h = metrics.get('high', 0)
        m = metrics.get('medium', 0)
        return max(0, 100 - c * 20 - h * 5 - m * 1)

    def _render_latest_findings(self, metrics: Dict) -> str:
        if not self.assessments:
            return ''
        findings = self.assessments[-1]['findings']
        order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
        findings = sorted(findings, key=lambda f: order.get(f.get('severity', 'INFO'), 9))
        rows = ''
        for f in findings[:50]:
            sev = f.get('severity', 'INFO')
            color = self.SEVERITY_COLORS.get(sev, '#64748b')
            title = html_lib.escape(str(f.get('title', f.get('operation', 'Unknown'))))
            asset = html_lib.escape(str(f.get('table', f.get('category', '—'))))
            rec   = html_lib.escape(str(f.get('recommendation', '—')))
            rows += f"""
            <tr>
                <td><span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44">{sev}</span></td>
                <td>{title}</td>
                <td style="color:#94a3b8">{asset}</td>
                <td style="color:#64748b;font-size:12px">{rec[:80]}{'…' if len(rec) > 80 else ''}</td>
            </tr>"""
        return rows

    def _render_history_rows(self, trends: Dict) -> str:
        rows = ''
        for i, entry in enumerate(reversed(trends['total'])):
            date     = html_lib.escape(str(entry['date']))
            critical = trends['critical'][-(i + 1)]['count']
            high     = trends['high'][-(i + 1)]['count']
            medium   = trends['medium'][-(i + 1)]['count']
            total    = entry['count']
            rows += f"""
            <tr>
                <td style="color:#94a3b8">{date}</td>
                <td style="color:#ef4444;font-weight:600">{critical}</td>
                <td style="color:#f97316;font-weight:600">{high}</td>
                <td style="color:#eab308">{medium}</td>
                <td style="font-weight:700;color:#e2e8f0">{total}</td>
            </tr>"""
        return rows

    def render_html(self) -> str:
        metrics = self.generate_metrics()
        trends  = self.generate_trends()
        score   = self._health_score(metrics) if metrics else 0
        now     = datetime.now().strftime('%Y-%m-%d %H:%M')

        if not metrics:
            return """<!DOCTYPE html><html><body style="background:#0d1117;color:#e2e8f0;font-family:monospace;padding:40px">
            <h1>🕶️ DarkScope</h1><p>No assessments found in the specified directory.</p></body></html>"""

        score_color = '#22c55e' if score >= 80 else '#eab308' if score >= 50 else '#ef4444'
        dates         = json.dumps([t['date'] for t in trends['total']])
        critical_data = json.dumps([t['count'] for t in trends['critical']])
        high_data     = json.dumps([t['count'] for t in trends['high']])
        medium_data   = json.dumps([t['count'] for t in trends['medium']])
        dist_data     = json.dumps([metrics['critical'], metrics['high'], metrics['medium'], metrics['low']])

        latest_rows  = self._render_latest_findings(metrics)
        history_rows = self._render_history_rows(trends)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DarkScope — Security Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0d1117; --surface: #161b22; --border: #21262d;
    --text: #e2e8f0; --muted: #64748b; --accent: #7c3aed;
  }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; min-height: 100vh; }}

  /* ─── Header ─── */
  .header {{
    background: linear-gradient(135deg, #0f0a1e 0%, #1a0a2e 50%, #0f1a2e 100%);
    border-bottom: 1px solid #7c3aed44;
    padding: 28px 40px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .header-left {{ display: flex; align-items: center; gap: 16px; }}
  .logo {{ font-size: 32px; }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #e2e8f0; letter-spacing: -0.5px; }}
  .header h1 span {{ color: #7c3aed; }}
  .header-meta {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
  .header-badge {{
    background: #7c3aed22; border: 1px solid #7c3aed55; color: #a78bfa;
    font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 20px;
    letter-spacing: 0.05em; text-transform: uppercase;
  }}

  /* ─── Layout ─── */
  .container {{ max-width: 1280px; margin: 0 auto; padding: 32px 40px; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }}
  .grid-3 {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 28px; }}

  /* ─── Cards ─── */
  .card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
  }}
  .card-title {{
    font-size: 11px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;
    display: flex; align-items: center; gap: 6px;
  }}
  .card-title::before {{ content: ''; display: inline-block; width: 3px; height: 12px; border-radius: 2px; background: var(--accent); }}

  /* ─── Metric tiles ─── */
  .metric-tile {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px 24px;
    display: flex; flex-direction: column; gap: 6px;
    position: relative; overflow: hidden;
  }}
  .metric-tile::after {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--tile-color, #7c3aed);
  }}
  .metric-tile .label {{ font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }}
  .metric-tile .value {{ font-size: 36px; font-weight: 800; color: var(--tile-color, #e2e8f0); line-height: 1; }}
  .metric-tile .sub {{ font-size: 11px; color: var(--muted); }}

  /* ─── Health ring ─── */
  .health-ring-wrap {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 8px; }}
  .health-score {{ font-size: 52px; font-weight: 800; color: {score_color}; line-height: 1; }}
  .health-label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }}
  .health-bar {{ width: 100%; height: 6px; background: #1e293b; border-radius: 3px; margin-top: 8px; overflow: hidden; }}
  .health-bar-fill {{ height: 100%; background: {score_color}; border-radius: 3px; transition: width 0.6s ease; }}

  /* ─── Charts ─── */
  .chart-wrap {{ position: relative; height: 240px; }}

  /* ─── Table ─── */
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ padding: 10px 14px; text-align: left; font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid var(--border); }}
  td {{ padding: 11px 14px; border-bottom: 1px solid #161b2266; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #ffffff04; }}
  .badge {{ padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; letter-spacing: 0.06em; white-space: nowrap; }}

  /* ─── Footer ─── */
  .footer {{ text-align: center; padding: 32px; color: var(--muted); font-size: 11px; border-top: 1px solid var(--border); margin-top: 20px; }}
</style>
</head>
<body>

<header class="header">
  <div class="header-left">
    <span class="logo">🕶️</span>
    <div>
      <h1>Dark<span>Scope</span> — Security Dashboard</h1>
      <div class="header-meta">Generated {now} · {metrics['total_assessments']} assessment{'s' if metrics['total_assessments'] != 1 else ''} tracked · Latest: {metrics['latest_date']}</div>
    </div>
  </div>
  <div class="header-badge">Confidential</div>
</header>

<div class="container">

  <!-- ─── Metric tiles ─── -->
  <div class="grid-4">
    <div class="metric-tile" style="--tile-color:#ef4444">
      <div class="label">Critical</div>
      <div class="value">{metrics['critical']}</div>
      <div class="sub">Immediate action required</div>
    </div>
    <div class="metric-tile" style="--tile-color:#f97316">
      <div class="label">High</div>
      <div class="value">{metrics['high']}</div>
      <div class="sub">Remediate within 30 days</div>
    </div>
    <div class="metric-tile" style="--tile-color:#eab308">
      <div class="label">Medium</div>
      <div class="value">{metrics['medium']}</div>
      <div class="sub">Remediate within 90 days</div>
    </div>
    <div class="metric-tile" style="--tile-color:#22d3ee">
      <div class="label">Low / Info</div>
      <div class="value">{metrics['low'] + metrics['info']}</div>
      <div class="sub">Track &amp; monitor</div>
    </div>
  </div>

  <!-- ─── Trends + Health ─── -->
  <div class="grid-3">
    <div class="card">
      <div class="card-title">Finding Trends</div>
      <div class="chart-wrap"><canvas id="trendsChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Security Health</div>
      <div class="health-ring-wrap">
        <div class="health-score">{score}</div>
        <div class="health-label">Health Score</div>
        <div class="health-bar"><div class="health-bar-fill" style="width:{score}%"></div></div>
        <div style="font-size:12px;color:{'#22c55e' if score >= 80 else '#eab308' if score >= 50 else '#ef4444'};margin-top:8px;font-weight:600">
          {'✅ Good posture' if score >= 80 else '⚠️ Needs attention' if score >= 50 else '🚨 Critical risk'}
        </div>
      </div>
    </div>
  </div>

  <!-- ─── Distribution + History ─── -->
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Severity Distribution</div>
      <div class="chart-wrap" style="height:200px"><canvas id="distChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Assessment History</div>
      <div style="overflow-x:auto">
        <table>
          <thead><tr><th>Date</th><th>Critical</th><th>High</th><th>Medium</th><th>Total</th></tr></thead>
          <tbody>{history_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ─── Latest findings table ─── -->
  <div class="card">
    <div class="card-title">Latest Findings — {metrics['latest_date']}</div>
    <div style="overflow-x:auto">
      <table>
        <thead><tr><th>Severity</th><th>Finding</th><th>Asset / Category</th><th>Recommendation</th></tr></thead>
        <tbody>{latest_rows if latest_rows else '<tr><td colspan="4" style="color:#64748b;text-align:center;padding:24px">No findings in latest assessment</td></tr>'}</tbody>
      </table>
    </div>
  </div>

</div>

<div class="footer">
  🕶️ DarkScope · This report contains sensitive security information · Distribute only to authorized personnel
</div>

<script>
const chartDefaults = {{
  responsive: true,
  maintainAspectRatio: false,
  plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 12 }} }} }} }},
  scales: {{
    x: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#64748b' }} }},
    y: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#64748b' }}, beginAtZero: true }}
  }}
}};

// Trends line chart
new Chart(document.getElementById('trendsChart'), {{
  type: 'line',
  data: {{
    labels: {dates},
    datasets: [
      {{ label: 'Critical', data: {critical_data}, borderColor: '#ef4444', backgroundColor: '#ef444422', tension: 0.4, fill: true, pointRadius: 4 }},
      {{ label: 'High',     data: {high_data},     borderColor: '#f97316', backgroundColor: '#f9731622', tension: 0.4, fill: true, pointRadius: 4 }},
      {{ label: 'Medium',   data: {medium_data},   borderColor: '#eab308', backgroundColor: '#eab30822', tension: 0.4, fill: true, pointRadius: 4 }},
    ]
  }},
  options: chartDefaults
}});

// Distribution doughnut
new Chart(document.getElementById('distChart'), {{
  type: 'doughnut',
  data: {{
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{{ data: {dist_data}, backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22d3ee'], borderWidth: 0, hoverOffset: 4 }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'right', labels: {{ color: '#94a3b8', padding: 16, font: {{ size: 12 }} }} }}
    }},
    cutout: '65%'
  }}
}});
</script>
</body>
</html>"""

    def save_html(self, output_file: Path) -> Path:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.render_html())
        return output_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate DarkScope security dashboard.")
    parser.add_argument("assessments_dir", help="Directory containing assessment reports (with findings.json files)")
    parser.add_argument("--output", default="dashboard.html", help="Output HTML file (default: dashboard.html)")
    args = parser.parse_args()

    assessments_dir = Path(args.assessments_dir)
    if not assessments_dir.exists():
        print(f"❌ Directory not found: {assessments_dir}")
        sys.exit(1)

    print(f"🕶️  DarkScope Dashboard Generator")
    print(f"   Scanning: {assessments_dir.resolve()}")

    dashboard = Dashboard(assessments_dir)

    if not dashboard.assessments:
        print(f"⚠️  No findings.json files found in {assessments_dir}")
        print(f"   Expected structure: {assessments_dir}/<date>/findings.json")
        sys.exit(1)

    print(f"   Found {len(dashboard.assessments)} assessment(s)")

    output_file = Path(args.output)
    dashboard.save_html(output_file)

    metrics = dashboard.generate_metrics()
    score   = dashboard._health_score(metrics)
    print(f"\n✅ Dashboard generated: {output_file.resolve()}")
    print(f"   Health Score: {score}/100")
    print(f"   Critical: {metrics['critical']}  High: {metrics['high']}  Medium: {metrics['medium']}  Low: {metrics['low']}")
    print(f"\n   Open in browser:")
    print(f"   file:///{output_file.resolve().as_posix()}")


if __name__ == "__main__":
    main()
