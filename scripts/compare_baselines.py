#!/usr/bin/env python3
"""
Compare security assessment baselines to track program progress.
Detects regressions, fixed findings, and new issues.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class BaselineComparator:
    """Compare current assessment to prior baselines"""

    def __init__(self, current_findings: List[Dict], prior_baseline: Optional[List[Dict]] = None):
        self.current = self._normalize_findings(current_findings)
        self.prior = self._normalize_findings(prior_baseline or [])

    @staticmethod
    def _normalize_findings(findings: List[Dict]) -> Dict[Tuple, Dict]:
        """Create a normalized dict keyed by (table, operation) for easy comparison"""
        normalized = {}
        for finding in findings:
            key = (finding.get('table'), finding.get('operation'))
            normalized[key] = finding
        return normalized

    def get_fixed_findings(self) -> List[Dict]:
        """Findings that were in prior but not in current"""
        return [f for key, f in self.prior.items() if key not in self.current]

    def get_new_findings(self) -> List[Dict]:
        """Findings that are in current but not in prior"""
        return [f for key, f in self.current.items() if key not in self.prior]

    def get_regressions(self) -> List[Tuple[Dict, Dict]]:
        """Findings that got worse (higher severity)"""
        severity_rank = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}

        regressions = []
        for key, current_f in self.current.items():
            if key in self.prior:
                prior_f = self.prior[key]
                current_severity = severity_rank.get(current_f.get('severity'), 0)
                prior_severity = severity_rank.get(prior_f.get('severity'), 0)

                if current_severity > prior_severity:
                    regressions.append((prior_f, current_f))

        return regressions

    def get_improvements(self) -> List[Tuple[Dict, Dict]]:
        """Findings that improved (lower severity)"""
        severity_rank = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}

        improvements = []
        for key, current_f in self.current.items():
            if key in self.prior:
                prior_f = self.prior[key]
                current_severity = severity_rank.get(current_f.get('severity'), 0)
                prior_severity = severity_rank.get(prior_f.get('severity'), 0)

                if current_severity < prior_severity:
                    improvements.append((prior_f, current_f))

        return improvements

    def compute_metrics(self) -> Dict:
        """Compute assessment metrics"""
        fixed = self.get_fixed_findings()
        new = self.get_new_findings()
        regressions = self.get_regressions()
        improvements = self.get_improvements()

        current_critical = len([f for f in self.current.values() if f.get('severity') == 'CRITICAL'])
        prior_critical = len([f for f in self.prior.values() if f.get('severity') == 'CRITICAL'])

        return {
            'timestamp': datetime.now().isoformat(),
            'current_total': len(self.current),
            'prior_total': len(self.prior),
            'fixed': len(fixed),
            'new': len(new),
            'regressions': len(regressions),
            'improvements': len(improvements),
            'current_critical': current_critical,
            'prior_critical': prior_critical,
            'critical_delta': current_critical - prior_critical,
            'health_trend': self._compute_health_trend()
        }

    def _compute_health_trend(self) -> str:
        """Determine if health is improving or degrading"""
        metrics = self.compute_metrics()

        if metrics['regressions'] > 0:
            return 'DEGRADING'
        elif metrics['fixed'] > 0 and metrics['new'] == 0:
            return 'IMPROVING'
        elif metrics['new'] > 0 and metrics['fixed'] == 0:
            return 'DEGRADING'
        elif metrics['new'] > metrics['fixed']:
            return 'DEGRADING'
        elif metrics['fixed'] > metrics['new']:
            return 'IMPROVING'
        else:
            return 'STABLE'

    def render_summary(self) -> str:
        """Render text summary"""
        metrics = self.compute_metrics()
        fixed = self.get_fixed_findings()
        new = self.get_new_findings()
        regressions = self.get_regressions()

        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║                   Baseline Comparison Report                   ║
╚════════════════════════════════════════════════════════════════╝

Assessment Timestamp: {metrics['timestamp']}

METRICS
{'=' * 50}
Current findings:     {metrics['current_total']}
Prior findings:       {metrics['prior_total']}

Fixed:               {metrics['fixed']} ✅
New:                 {metrics['new']} 🆕
Regressions:         {metrics['regressions']} ⚠️
Improvements:        {metrics['improvements']} 📈

Critical Findings:
  Prior:             {metrics['prior_critical']}
  Current:           {metrics['current_critical']}
  Delta:             {metrics['critical_delta']:+d}

Health Trend:        {metrics['health_trend']}
"""

        if fixed:
            summary += f"""
FIXED FINDINGS ({len(fixed)})
{'=' * 50}
"""
            for finding in fixed:
                summary += f"  ✅ {finding.get('table')}: {finding.get('operation')} ({finding.get('severity')})\n"

        if new:
            summary += f"""
NEW FINDINGS ({len(new)})
{'=' * 50}
"""
            for finding in new:
                summary += f"  🆕 {finding.get('table')}: {finding.get('operation')} ({finding.get('severity')})\n"

        if regressions:
            summary += f"""
REGRESSIONS ({len(regressions)})
{'=' * 50}
"""
            for prior_f, current_f in regressions:
                summary += f"  ⚠️  {prior_f.get('table')}: {prior_f.get('operation')}\n"
                summary += f"      {prior_f.get('severity')} → {current_f.get('severity')}\n"

        return summary

    def render_json(self) -> Dict:
        """Render as JSON for machine parsing"""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.compute_metrics(),
            'fixed': self.get_fixed_findings(),
            'new': self.get_new_findings(),
            'regressions': [
                {'prior': p, 'current': c} for p, c in self.get_regressions()
            ],
            'improvements': [
                {'prior': p, 'current': c} for p, c in self.get_improvements()
            ]
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compare DarkScope assessment baselines.")
    parser.add_argument("--current", required=True, help="Current findings JSON file")
    parser.add_argument("--prior", help="Prior baseline JSON file")
    parser.add_argument("--output", help="Output comparison JSON file")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit with code 1 if regressions found")
    args = parser.parse_args()

    # Load findings
    with open(args.current) as f:
        current = json.load(f)

    prior = None
    if args.prior:
        with open(args.prior) as f:
            prior = json.load(f)

    # Ensure current is a list of findings
    if isinstance(current, dict) and 'findings' in current:
        current = current['findings']
    if prior and isinstance(prior, dict) and 'findings' in prior:
        prior = prior['findings']

    # Compare
    comparator = BaselineComparator(current, prior or [])

    # Print summary
    print(comparator.render_summary())

    # Save JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(comparator.render_json(), f, indent=2)
        print(f"\n✅ Comparison saved to: {args.output}")

    # Exit with error if regressions found
    if args.fail_on_regression:
        metrics = comparator.compute_metrics()
        if metrics['regressions'] > 0:
            print(f"\n❌ REGRESSION DETECTED: {metrics['regressions']} findings got worse")
            sys.exit(1)
        elif metrics['critical_delta'] > 0:
            print(f"\n❌ REGRESSION DETECTED: Critical findings increased by {metrics['critical_delta']}")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
