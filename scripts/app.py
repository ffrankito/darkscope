#!/usr/bin/env python3
"""
DarkScope — local dashboard server
Usage: python scripts/app.py [--dir ./results] [--port 5000]
"""

import json
import sys
import argparse
import threading
import webbrowser
from pathlib import Path
from collections import defaultdict
from flask import Flask, jsonify

app = Flask(__name__)
ASSESSMENTS_DIR = Path('./results')


# ── Data loading ─────────────────────────────────────────────────────────────

def load_assessments(base_dir: Path):
    assessments = []
    for findings_file in sorted(base_dir.glob('**/findings.json')):
        try:
            raw = json.loads(findings_file.read_text(encoding='utf-8'))
            findings = raw if isinstance(raw, list) else raw.get('findings', [])
            assessments.append({
                'date': findings_file.parent.name,
                'findings': findings,
            })
        except Exception:
            pass
    return sorted(assessments, key=lambda a: a['date'])


def counts_for(findings):
    c = defaultdict(int)
    for f in findings:
        c[f.get('severity', 'INFO')] += 1
    return {
        'critical': c['CRITICAL'],
        'high':     c['HIGH'],
        'medium':   c['MEDIUM'],
        'low':      c['LOW'],
        'info':     c['INFO'],
    }


def health_score(counts):
    return max(0, 100 - counts['critical'] * 20 - counts['high'] * 5 - counts['medium'] * 1)


# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/data')
def api_data():
    assessments = load_assessments(ASSESSMENTS_DIR)

    if not assessments:
        return jsonify({'assessments': [], 'latest': None})

    trend = []
    for a in assessments:
        c = counts_for(a['findings'])
        trend.append({
            'date':     a['date'],
            'critical': c['critical'],
            'high':     c['high'],
            'medium':   c['medium'],
            'low':      c['low'],
            'total':    sum(c.values()),
        })

    latest = assessments[-1]
    lc = counts_for(latest['findings'])

    # Normalize findings fields so the frontend always gets consistent keys
    normalized = []
    for f in latest['findings']:
        normalized.append({
            'severity':       f.get('severity', 'INFO'),
            'title':          f.get('title', f.get('operation', 'Unknown finding')),
            'asset':          f.get('table', f.get('category', f.get('target', '—'))),
            'recommendation': f.get('recommendation', '—'),
        })

    return jsonify({
        'assessments': trend,
        'latest': {
            'date':         latest['date'],
            'findings':     normalized,
            'counts':       lc,
            'health_score': health_score(lc),
        }
    })


# ── HTML (single-page app) ────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DarkScope</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg:     #080c15;
  --surf:   #0d1625;
  --surf2:  #121e35;
  --border: #1a2840;
  --bord2:  #243554;
  --text:   #dce6f5;
  --muted:  #4a6080;
  --dim:    #2a3e5a;
  --accent: #4f7cff;
  --crit:   #f43f5e;
  --high:   #fb923c;
  --med:    #fbbf24;
  --low:    #34d399;
  font-variant-numeric: tabular-nums;
}
body {
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size: 13px;
  line-height: 1.5;
  min-height: 100vh;
}

/* Header */
.hdr {
  height: 52px;
  background: var(--surf);
  border-bottom: 1px solid var(--border);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
  background-image: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(79,124,255,.016) 2px, rgba(79,124,255,.016) 4px
  );
}
.hdr-left { display: flex; align-items: center; gap: 14px; }
.wordmark {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: .14em;
  color: var(--text);
}
.wordmark em { color: var(--accent); font-style: normal; }
.hdr-sep { width: 1px; height: 18px; background: var(--bord2); }
.hdr-sub { font-size: 11px; color: var(--muted); letter-spacing: .04em; }
.hdr-right { display: flex; align-items: center; gap: 14px; }
.live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--low);
  box-shadow: 0 0 6px var(--low);
  animation: blink 2.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
.conf {
  font-size: 10px; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: var(--muted);
  border: 1px solid var(--bord2); padding: 3px 10px; border-radius: 2px;
}

/* Layout */
.wrap { max-width: 1320px; margin: 0 auto; padding: 24px 28px 48px; }

/* Metric strip */
.strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 20px;
}
.cell {
  background: var(--surf);
  padding: 14px 18px;
  position: relative;
}
.cell::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 2px;
  background: var(--c, var(--accent));
}
.cell-label { font-size: 10px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: 5px; }
.cell-value { font-family: 'Courier New', monospace; font-size: 30px; font-weight: 700; line-height: 1; color: var(--c, var(--text)); }
.cell-sub   { font-size: 10px; color: var(--muted); margin-top: 3px; }

/* Section label */
.slabel {
  font-size: 10px; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: var(--muted);
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
}
.slabel::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* Charts row */
.charts { display: grid; grid-template-columns: 1fr 260px; gap: 14px; margin-bottom: 20px; }
.panel { background: var(--surf); border: 1px solid var(--border); border-radius: 3px; padding: 18px 20px; }
.panel-title { font-size: 10px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: 14px; }

/* Donut panel */
.donut-panel { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; }
.health-num { font-family: 'Courier New', monospace; font-size: 44px; font-weight: 700; line-height: 1; text-align: center; }
.health-lbl { font-size: 10px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); text-align: center; margin-top: 2px; }
.hbar { width: 100%; height: 3px; background: var(--bord2); border-radius: 2px; overflow: hidden; }
.hbar-fill { height: 100%; border-radius: 2px; }
.legend { width: 100%; display: flex; flex-direction: column; gap: 6px; }
.leg-row { display: flex; align-items: center; gap: 7px; font-size: 11px; }
.leg-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.leg-name { flex: 1; color: var(--muted); }
.leg-n { font-family: 'Courier New', monospace; font-weight: 600; }

/* Findings */
.tabs { display: flex; gap: 3px; flex-wrap: wrap; margin-bottom: 14px; }
.tab {
  font-size: 10px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; padding: 4px 11px;
  border: 1px solid var(--bord2); border-radius: 2px;
  background: transparent; color: var(--muted); cursor: pointer;
  transition: background .12s, color .12s, border-color .12s;
}
.tab:hover { background: var(--surf2); color: var(--text); }
.tab.on { background: var(--surf2); color: var(--text); }
.tab[data-s="ALL"].on    { color: var(--accent); border-color: var(--accent); }
.tab[data-s="CRITICAL"].on { color: var(--crit); border-color: var(--crit); background: #f43f5e0d; }
.tab[data-s="HIGH"].on     { color: var(--high); border-color: var(--high); background: #fb923c0d; }
.tab[data-s="MEDIUM"].on   { color: var(--med);  border-color: var(--med);  background: #fbbf240d; }
.tab[data-s="LOW"].on      { color: var(--low);  border-color: var(--low);  background: #34d3990d; }
.tbl-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th {
  padding: 7px 12px; text-align: left;
  font-size: 10px; font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
  color: var(--muted); border-bottom: 1px solid var(--border); white-space: nowrap;
}
td { padding: 10px 12px; border-bottom: 1px solid #0d162520; vertical-align: top; }
tr.fr:hover td { background: #121e3530; }
tr.fr[hidden] { display: none; }
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 700; letter-spacing: .07em;
  padding: 2px 6px; border-radius: 2px; white-space: nowrap;
}
.badge::before { content: ''; display: block; width: 4px; height: 4px; border-radius: 50%; background: currentColor; }
.CRITICAL { color: var(--crit); background: #f43f5e12; border: 1px solid #f43f5e28; }
.HIGH     { color: var(--high); background: #fb923c12; border: 1px solid #fb923c28; }
.MEDIUM   { color: var(--med);  background: #fbbf2412; border: 1px solid #fbbf2428; }
.LOW      { color: var(--low);  background: #34d39912; border: 1px solid #34d39928; }
.INFO     { color: var(--muted);background: #64748b12; border: 1px solid #64748b28; }
.ftitle { color: var(--text); font-size: 12.5px; }
.fasset { color: var(--muted); font-family: 'Courier New', monospace; font-size: 11px; }
.frec   { color: var(--dim); font-size: 12px; max-width: 340px; }

/* Empty / error states */
.state-msg { padding: 48px 0; text-align: center; color: var(--muted); font-size: 13px; }
</style>
</head>
<body>

<header class="hdr">
  <div class="hdr-left">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="#4f7cff" stroke-width="1.5"/>
      <circle cx="12" cy="12" r="5"  stroke="#4f7cff" stroke-width="1" stroke-dasharray="2 2"/>
      <circle cx="12" cy="12" r="1.5" fill="#4f7cff"/>
      <line x1="2" y1="12" x2="7"  y2="12" stroke="#4f7cff" stroke-width="1.5"/>
      <line x1="17" y1="12" x2="22" y2="12" stroke="#4f7cff" stroke-width="1.5"/>
    </svg>
    <span class="wordmark">DARK<em>SCOPE</em></span>
    <div class="hdr-sep"></div>
    <span class="hdr-sub" id="hdrMeta">Loading…</span>
  </div>
  <div class="hdr-right">
    <div class="live-dot" title="Connected"></div>
    <span class="conf">Confidential</span>
  </div>
</header>

<main class="wrap">

  <!-- Metric strip -->
  <div class="strip" id="strip">
    <div class="cell" style="--c:var(--crit)"><div class="cell-label">Critical</div><div class="cell-value" id="vCrit">—</div><div class="cell-sub">Immediate action</div></div>
    <div class="cell" style="--c:var(--high)"><div class="cell-label">High</div><div class="cell-value" id="vHigh">—</div><div class="cell-sub">30 days</div></div>
    <div class="cell" style="--c:var(--med)"> <div class="cell-label">Medium</div><div class="cell-value" id="vMed">—</div><div class="cell-sub">90 days</div></div>
    <div class="cell" style="--c:var(--low)"> <div class="cell-label">Low</div><div class="cell-value" id="vLow">—</div><div class="cell-sub">Track</div></div>
    <div class="cell" style="--c:var(--accent)"><div class="cell-label">Health Score</div><div class="cell-value" id="vScore">—</div><div class="cell-sub" id="vScoreSub"></div></div>
  </div>

  <!-- Charts -->
  <div class="slabel" id="trendLabel">Trend</div>
  <div class="charts">
    <div class="panel">
      <div class="panel-title">Findings over time</div>
      <canvas id="trendC" style="display:block;width:100%;height:200px"></canvas>
    </div>
    <div class="panel donut-panel">
      <canvas id="donutC" width="120" height="120"></canvas>
      <div>
        <div class="health-num" id="healthNum">—</div>
        <div class="health-lbl">Health Score</div>
      </div>
      <div class="hbar"><div class="hbar-fill" id="hbarFill" style="width:0"></div></div>
      <div class="legend" id="legend"></div>
    </div>
  </div>

  <!-- Findings -->
  <div class="slabel" id="findingsLabel">Findings</div>
  <div class="panel">
    <div class="tabs" id="tabs"></div>
    <div class="tbl-wrap">
      <table>
        <thead>
          <tr><th>Severity</th><th>Finding</th><th>Asset / Category</th><th>Recommendation</th></tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </div>

</main>

<script>
const SEV_COLOR = { CRITICAL:'#f43f5e', HIGH:'#fb923c', MEDIUM:'#fbbf24', LOW:'#34d399', INFO:'#64748b' };

async function load() {
  let data;
  try {
    const r = await fetch('/api/data');
    if (!r.ok) throw new Error(r.status);
    data = await r.json();
  } catch(e) {
    document.getElementById('hdrMeta').textContent = 'Error loading data — is the server running?';
    return;
  }

  if (!data.latest) {
    document.getElementById('hdrMeta').textContent = 'No assessments found in results/';
    document.getElementById('tbody').innerHTML = '<tr><td colspan="4" class="state-msg">Run an assessment first:<br><code>python scripts/run_assessment.py https://target.com --level 2</code></td></tr>';
    return;
  }

  const { assessments, latest } = data;
  const { counts, health_score, date, findings } = latest;

  // Header
  document.getElementById('hdrMeta').textContent =
    `${assessments.length} assessment${assessments.length !== 1 ? 's' : ''} · latest: ${date}`;

  // Strip
  document.getElementById('vCrit').textContent  = counts.critical;
  document.getElementById('vHigh').textContent  = counts.high;
  document.getElementById('vMed').textContent   = counts.medium;
  document.getElementById('vLow').textContent   = counts.low;
  document.getElementById('vScore').textContent = health_score;
  const scoreColor = health_score >= 80 ? '#34d399' : health_score >= 50 ? '#fbbf24' : '#f43f5e';
  document.querySelector('#strip .cell:last-child .cell-value').style.color = scoreColor;
  document.getElementById('vScoreSub').textContent =
    health_score >= 80 ? 'Good posture' : health_score >= 50 ? 'Needs attention' : 'Critical risk';

  // Health panel
  document.getElementById('healthNum').textContent  = health_score;
  document.getElementById('healthNum').style.color  = scoreColor;
  document.getElementById('hbarFill').style.width    = health_score + '%';
  document.getElementById('hbarFill').style.background = scoreColor;

  // Legend
  const legEl = document.getElementById('legend');
  [['critical','Critical',counts.critical],['high','High',counts.high],
   ['medium','Medium',counts.medium],['low','Low',counts.low]].forEach(([key, label, n]) => {
    const row = document.createElement('div');
    row.className = 'leg-row';
    row.innerHTML = `<div class="leg-dot" style="background:${SEV_COLOR[key.toUpperCase()]}"></div>
                     <span class="leg-name">${label}</span><span class="leg-n">${n}</span>`;
    legEl.appendChild(row);
  });

  // Donut
  drawDonut(counts);

  // Trend chart
  if (assessments.length >= 2) {
    document.getElementById('trendLabel').textContent = `Trend · ${assessments.length} assessments`;
    drawTrend(assessments);
  } else {
    const c = document.getElementById('trendC');
    c.style.height = '48px';
    const ctx = c.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    c.width = c.parentElement.clientWidth * dpr;
    c.height = 48 * dpr;
    ctx.scale(dpr, dpr);
    ctx.fillStyle = '#4a6080';
    ctx.font = '12px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText('Run more assessments to see trends', c.parentElement.clientWidth / 2, 24);
  }

  // Findings label
  document.getElementById('findingsLabel').textContent =
    `Findings · ${date} · ${findings.length} total`;

  // Filter tabs
  const tabs = document.getElementById('tabs');
  const sevCounts = {};
  findings.forEach(f => { sevCounts[f.severity] = (sevCounts[f.severity] || 0) + 1; });
  const order = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];
  order.forEach(s => {
    const count = s === 'ALL' ? findings.length : (sevCounts[s] || 0);
    if (s !== 'ALL' && !count) return;
    const btn = document.createElement('button');
    btn.className = 'tab' + (s === 'ALL' ? ' on' : '');
    btn.dataset.s = s;
    btn.textContent = `${s} (${count})`;
    btn.addEventListener('click', () => {
      tabs.querySelectorAll('.tab').forEach(t => t.classList.remove('on'));
      btn.classList.add('on');
      document.querySelectorAll('tr.fr').forEach(tr => {
        tr.hidden = s !== 'ALL' && tr.dataset.s !== s;
      });
    });
    tabs.appendChild(btn);
  });

  // Findings table
  const tbody = document.getElementById('tbody');
  if (!findings.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="state-msg">No findings in this assessment</td></tr>';
    return;
  }
  const sevOrder = { CRITICAL:0, HIGH:1, MEDIUM:2, LOW:3, INFO:4 };
  const sorted = [...findings].sort((a,b) =>
    (sevOrder[a.severity] ?? 9) - (sevOrder[b.severity] ?? 9));
  sorted.forEach(f => {
    const tr = document.createElement('tr');
    tr.className = 'fr';
    tr.dataset.s = f.severity;
    const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    tr.innerHTML = `
      <td><span class="badge ${esc(f.severity)}">${esc(f.severity)}</span></td>
      <td class="ftitle">${esc(f.title)}</td>
      <td class="fasset">${esc(f.asset)}</td>
      <td class="frec">${esc(f.recommendation)}</td>`;
    tbody.appendChild(tr);
  });
}

function drawTrend(data) {
  const canvas = document.getElementById('trendC');
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.parentElement.clientWidth - 40;
  const H = 200;
  canvas.width  = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const pad = { t:14, r:20, b:30, l:34 };
  const cw = W - pad.l - pad.r;
  const ch = H - pad.t  - pad.b;
  const n  = data.length;
  const maxV = Math.max(...data.flatMap(d => [d.critical, d.high, d.medium]), 4);

  const xOf = i => pad.l + (i / (n - 1)) * cw;
  const yOf = v => pad.t + (1 - v / maxV) * ch;

  // Grid
  for (let s = 0; s <= 4; s++) {
    const v = (maxV / 4) * s;
    const y = yOf(v);
    ctx.strokeStyle = '#1a284030'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + cw, y); ctx.stroke();
    ctx.fillStyle = '#4a6080'; ctx.font = '10px system-ui'; ctx.textAlign = 'right';
    ctx.fillText(Math.round(v), pad.l - 5, y + 3.5);
  }

  // X labels
  data.forEach((d, i) => {
    ctx.fillStyle = '#4a6080'; ctx.font = '10px system-ui'; ctx.textAlign = 'center';
    const label = d.date.slice(0, 10); // first 10 chars
    ctx.fillText(label.slice(-5), xOf(i), H - 7); // show MM-DD or similar
  });

  function drawLine(series, color) {
    const vals = data.map(d => d[series]);
    const grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + ch);
    grad.addColorStop(0, color + '22'); grad.addColorStop(1, color + '00');
    ctx.beginPath();
    ctx.moveTo(xOf(0), yOf(vals[0]));
    for (let i = 1; i < n; i++) {
      const mx = (xOf(i-1) + xOf(i)) / 2;
      ctx.bezierCurveTo(mx, yOf(vals[i-1]), mx, yOf(vals[i]), xOf(i), yOf(vals[i]));
    }
    ctx.lineTo(xOf(n-1), yOf(0)); ctx.lineTo(xOf(0), yOf(0)); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath();
    ctx.moveTo(xOf(0), yOf(vals[0]));
    for (let i = 1; i < n; i++) {
      const mx = (xOf(i-1) + xOf(i)) / 2;
      ctx.bezierCurveTo(mx, yOf(vals[i-1]), mx, yOf(vals[i]), xOf(i), yOf(vals[i]));
    }
    ctx.strokeStyle = color; ctx.lineWidth = 1.8; ctx.stroke();
    // Endpoint
    const ex = xOf(n-1), ey = yOf(vals[n-1]);
    ctx.beginPath(); ctx.arc(ex, ey, 4, 0, Math.PI*2); ctx.fillStyle = color; ctx.fill();
    ctx.beginPath(); ctx.arc(ex, ey, 2, 0, Math.PI*2); ctx.fillStyle = '#080c15'; ctx.fill();
  }

  drawLine('medium',   '#fbbf24');
  drawLine('high',     '#fb923c');
  drawLine('critical', '#f43f5e');
}

function drawDonut(counts) {
  const canvas = document.getElementById('donutC');
  const dpr = window.devicePixelRatio || 1;
  const S = 120;
  canvas.width = S * dpr; canvas.height = S * dpr;
  canvas.style.width = S + 'px'; canvas.style.height = S + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const cx = S/2, cy = S/2, r = 50, ir = 32;
  const slices = [
    [counts.critical, '#f43f5e'],
    [counts.high,     '#fb923c'],
    [counts.medium,   '#fbbf24'],
    [counts.low,      '#34d399'],
  ].filter(s => s[0] > 0);

  const total = slices.reduce((a, s) => a + s[0], 0);
  if (!total) return;

  let angle = -Math.PI / 2;
  slices.forEach(([v, color]) => {
    const slice = (v / total) * Math.PI * 2;
    ctx.beginPath(); ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, angle, angle + slice); ctx.closePath();
    ctx.fillStyle = color; ctx.fill();
    angle += slice;
  });

  ctx.beginPath(); ctx.arc(cx, cy, ir, 0, Math.PI*2);
  ctx.fillStyle = '#0d1625'; ctx.fill();

  ctx.fillStyle = '#dce6f5';
  ctx.font = `bold 18px 'Courier New', monospace`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(total, cx, cy - 1);
  ctx.font = '9px system-ui'; ctx.fillStyle = '#4a6080';
  ctx.fillText('TOTAL', cx, cy + 12);
}

load();
// Auto-refresh every 30s so new assessment results show up automatically
setInterval(load, 30000);
</script>
</body>
</html>"""


# ── Route ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return HTML


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    global ASSESSMENTS_DIR

    parser = argparse.ArgumentParser(description='DarkScope local dashboard server')
    parser.add_argument('--dir',  default='./results', help='Assessments directory (default: ./results)')
    parser.add_argument('--port', type=int, default=5000, help='Port (default: 5000)')
    args = parser.parse_args()

    ASSESSMENTS_DIR = Path(args.dir)

    if not ASSESSMENTS_DIR.exists():
        print(f'⚠️  Directory not found: {ASSESSMENTS_DIR.resolve()}')
        print(f'   The dashboard will show an empty state until you run an assessment.')

    url = f'http://localhost:{args.port}'
    print(f'\n🕶️  DarkScope Dashboard')
    print(f'   Serving: {url}')
    print(f'   Data dir: {ASSESSMENTS_DIR.resolve()}')
    print(f'   Auto-refresh: every 30s\n')
    print(f'   Ctrl+C to stop\n')

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host='127.0.0.1', port=args.port, debug=False)


if __name__ == '__main__':
    main()
