#!/usr/bin/env python3
"""
DarkScope Main Assessment Orchestrator
Coordinates all assessment phases: auth → discovery → testing → reporting
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from request_authorization import AuthorizationManager
from check_tools import ToolChecker
from probe_supabase import SupabaseProber
from sanitize_evidence import EvidenceSanitizer
from generate_report_v2 import ReportGenerator
from compare_baselines import BaselineComparator
from plugin_manager import PluginManager

class AssessmentOrchestrator:
    """Orchestrate a complete security assessment"""

    LEVELS = {
        0: "Passive Orientation",
        1: "Safe Production Baseline",
        2: "Standard Production",
        3: "Deep Controlled Testing",
        4: "Aggressive Lab",
        5: "Enterprise Assurance"
    }

    def __init__(self, target: str, level: int = 2, env: str = "production", name: Optional[str] = None):
        self.target = target
        self.level = level
        self.env = env
        self.name = name or self._generate_name()
        self.assessment_dir = Path(f"./results/{self.name}")
        self.logger = self._setup_logging()
        self.findings = []

    def _generate_name(self) -> str:
        """Generate assessment directory name"""
        domain = self.target.replace("https://", "").replace("http://", "").split("/")[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{domain}_{timestamp}"

    def _setup_logging(self) -> logging.Logger:
        """Setup logging to file and console"""
        self.assessment_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.assessment_dir / "assessment.log"

        logger = logging.getLogger("darkscope")
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        logger.handlers = []

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def run(self, authorized: bool = False, execute: bool = False, supabase_config: Optional[Dict] = None) -> bool:
        """Execute full assessment workflow"""
        print(f"\n🕶️  DarkScope Assessment\n")
        print(f"Target:        {self.target}")
        print(f"Level:         {self.level} ({self.LEVELS[self.level]})")
        print(f"Environment:   {self.env}")
        print(f"Results dir:   {self.assessment_dir}\n")

        try:
            # Phase 1: Authorization
            if not authorized:
                self.logger.info("Phase 1: Authorization")
                if not self._request_authorization():
                    print("❌ Assessment cancelled by user")
                    return False

            # Phase 2: Check tools
            self.logger.info("Phase 2: Tool verification")
            self._verify_tools()

            # Phase 3: Testing
            if execute:
                self.logger.info("Phase 3: Security testing")
                self.findings = self._testing_phase()
                self.logger.info(f"Found {len(self.findings)} security findings")
            else:
                self.logger.info("Phase 3: Dry-run mode (no tests executed)")

            # Phase 4: Supabase testing
            if supabase_config and execute:
                self.logger.info("Phase 4: Supabase RLS testing")
                supabase_findings = self._test_supabase(supabase_config)
                self.findings.extend(supabase_findings)

            # Phase 5: Plugin system
            if execute:
                self.logger.info("Phase 5: Plugin system")
                plugin_findings = self._run_plugins()
                self.findings.extend(plugin_findings)

            # Phase 6: Evidence sanitization
            self.logger.info("Phase 6: Evidence sanitization")
            self._sanitize_evidence()

            # Phase 7: Reporting
            self.logger.info("Phase 7: Report generation")
            self._generate_reports()

            # Phase 8: Baseline comparison
            prior_baseline = self._find_prior_baseline()
            if prior_baseline:
                self.logger.info("Phase 8: Baseline comparison")
                self._compare_baselines(prior_baseline)

            # Summary
            print(f"\n{'='*60}")
            print(f"✅ Assessment Complete")
            print(f"{'='*60}")
            print(f"Results:       {self.assessment_dir}")
            print(f"Findings:      {len(self.findings)}")
            if self.findings:
                critical = len([f for f in self.findings if f.get('severity') == 'CRITICAL'])
                high = len([f for f in self.findings if f.get('severity') == 'HIGH'])
                print(f"  Critical:    {critical}")
                print(f"  High:        {high}")
            print(f"Log:           {self.assessment_dir / 'assessment.log'}\n")

            return True

        except Exception as e:
            self.logger.error(f"Assessment failed: {e}", exc_info=True)
            print(f"❌ Assessment failed: {e}")
            return False

    def _request_authorization(self) -> bool:
        """Request and log authorization"""
        manager = AuthorizationManager(self.target, self.level, self.env)
        return manager.request_confirmation()

    def _verify_tools(self) -> None:
        """Check if required tools are available"""
        checker = ToolChecker()
        missing = checker.check_level(self.level)
        if missing:
            print(f"⚠️  Missing tools for level {self.level}: {', '.join(missing)}")
        else:
            print(f"✅ All tools available for level {self.level}")

    def _testing_phase(self) -> List[Dict]:
        """Execute security tests"""
        findings = []
        self.logger.info("Testing phase started")
        return findings

    def _test_supabase(self, config: Dict) -> List[Dict]:
        """Test Supabase RLS policies"""
        prober = SupabaseProber(
            config['project_ref'],
            config['anon_key'],
            verify_ssl=config.get('verify_ssl', True)
        )
        return prober.test_all_tables()

    def _run_plugins(self) -> List[Dict]:
        """Run plugin system"""
        manager = PluginManager()
        return manager.run_all(self.target, self.level)

    def _sanitize_evidence(self) -> None:
        """Redact PII from findings"""
        sanitizer = EvidenceSanitizer()
        for finding in self.findings:
            if 'evidence' in finding and isinstance(finding['evidence'], dict):
                finding['evidence'] = sanitizer.sanitize_dict(finding['evidence'])

    def _generate_reports(self) -> None:
        """Generate HTML/PDF/JSON reports"""
        findings_file = self.assessment_dir / "findings.json"

        # Save findings
        with open(findings_file, 'w') as f:
            json.dump(self.findings, f, indent=2)
        self.logger.info(f"Findings saved: {findings_file}")

        # Generate HTML report
        generator = ReportGenerator(self.findings, level=self.level)
        html_file = self.assessment_dir / "report.html"
        generator.save_html(html_file)
        self.logger.info(f"HTML report: {html_file}")

        # Generate PDF if level >= 5
        if self.level >= 5:
            pdf_file = self.assessment_dir / "report.pdf"
            generator.save_pdf(pdf_file)
            if pdf_file.exists():
                self.logger.info(f"PDF report: {pdf_file}")

    def _find_prior_baseline(self) -> Optional[Path]:
        """Find previous assessment results"""
        results_dir = Path("./results")
        if not results_dir.exists():
            return None
        baselines = sorted(results_dir.glob("**/findings.json"))
        if len(baselines) > 1:
            return baselines[-2]
        return None

    def _compare_baselines(self, prior_baseline: Path) -> None:
        """Compare with prior assessment"""
        if not prior_baseline.exists():
            return

        current_findings = self.assessment_dir / "findings.json"
        with open(current_findings) as f:
            current = json.load(f)
        with open(prior_baseline) as f:
            prior = json.load(f)

        comparator = BaselineComparator(current, prior)
        comparison = comparator.render_json()
        comparison_file = self.assessment_dir / "comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)

        self.logger.info(f"Comparison saved to {comparison_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run DarkScope security assessment")
    parser.add_argument("target", help="Target URL (e.g., https://example.com)")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2, help="Assessment level (0-5)")
    parser.add_argument("--env", choices=["production", "staging", "lab"], default="production", help="Environment")
    parser.add_argument("--name", help="Assessment name (auto-generated if not provided)")
    parser.add_argument("--authorized", action="store_true", help="Skip authorization prompt")
    parser.add_argument("--execute", action="store_true", help="Execute tests (dry-run by default)")
    parser.add_argument("--supabase-project", help="Supabase project ref")
    parser.add_argument("--supabase-key", help="Supabase anon key")
    args = parser.parse_args()

    orchestrator = AssessmentOrchestrator(
        args.target,
        level=args.level,
        env=args.env,
        name=args.name
    )

    supabase_config = None
    if args.supabase_project and args.supabase_key:
        supabase_config = {
            'project_ref': args.supabase_project,
            'anon_key': args.supabase_key,
            'verify_ssl': True
        }

    success = orchestrator.run(
        authorized=args.authorized,
        execute=args.execute,
        supabase_config=supabase_config
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
