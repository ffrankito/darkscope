#!/usr/bin/env python3
"""
Code Analysis Phase: Static security analysis and dependency scanning
Uses: semgrep, trivy, npm audit, pip audit
"""

import json
import subprocess
import re
from typing import List, Dict, Any
from pathlib import Path
import tempfile
import shutil

from check_tools import find_tool


class CodeAnalysisPhase:
    """Execute code security analysis"""

    def __init__(self, target: str, level: int = 3, timeout: int = 900):
        self.target = target
        self.level = level
        self.timeout = timeout
        self.findings = []

    def run(self, repo_path: str = ".") -> List[Dict[str, Any]]:
        """Execute code analysis"""
        print(f"\n🔬 Code Analysis Phase (Level {self.level})")
        print(f"   Repository: {repo_path}\n")

        repo_path = Path(repo_path)
        if not repo_path.exists():
            print("   ⚠️  Repository path not found")
            return []

        # Level 3+: Static analysis with semgrep
        if self.level >= 3:
            self._semgrep_analysis(repo_path)

        # Level 3+: Dependency scanning
        if self.level >= 3:
            self._npm_audit(repo_path)
            self._pip_audit(repo_path)

        # Level 4+: Container scanning
        if self.level >= 4:
            self._trivy_scan(repo_path)

        return self.findings

    def _semgrep_analysis(self, repo_path: Path) -> None:
        """Run semgrep static analysis"""
        semgrep = find_tool("semgrep")
        if not semgrep:
            return

        print("   ├─ Semgrep static analysis...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [semgrep, "--config=p/owasp-top-ten", "--json", str(repo_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                issues = self._parse_semgrep(result.stdout)
                print(f"✅ ({len(issues)} issues)")

                for issue in issues:
                    self.findings.append({
                        "title": issue["title"],
                        "severity": issue["severity"],
                        "category": "code_quality",
                        "evidence": {
                            "file": issue["file"],
                            "line": issue["line"],
                            "rule": issue["rule"]
                        },
                        "recommendation": issue.get("recommendation", "Review and fix")
                    })
            else:
                print("⚠️")

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_semgrep(self, output: str) -> List[Dict]:
        """Parse semgrep JSON output"""
        issues = []
        try:
            data = json.loads(output)
            for result in data.get("results", []):
                severity = "MEDIUM"
                if result.get("extra", {}).get("severity") == "ERROR":
                    severity = "HIGH"

                issues.append({
                    "title": result.get("check_id", "Unknown"),
                    "severity": severity,
                    "file": result.get("path", ""),
                    "line": result.get("start", {}).get("line", 0),
                    "rule": result.get("check_id", ""),
                    "recommendation": "Review code pattern"
                })
        except:
            pass

        return issues

    def _npm_audit(self, repo_path: Path) -> None:
        """Audit npm dependencies"""
        package_json = repo_path / "package.json"
        if not package_json.exists():
            return

        npm = find_tool("npm")
        if not npm:
            return

        print("   ├─ NPM audit...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [npm, "audit", "--json"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=300
            )

            vulns = self._parse_npm_audit(result.stdout)
            print(f"✅ ({len(vulns)} vulnerabilities)")

            for vuln in vulns:
                self.findings.append({
                    "title": f"Vulnerable NPM package: {vuln['package']}",
                    "severity": vuln["severity"],
                    "category": "dependency",
                    "evidence": {
                        "package": vuln["package"],
                        "version": vuln["version"],
                        "vulnerability": vuln["id"]
                    },
                    "recommendation": f"Update {vuln['package']} to patched version"
                })

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_npm_audit(self, output: str) -> List[Dict]:
        """Parse npm audit JSON output"""
        vulns = []
        try:
            data = json.loads(output)
            for vuln_id, vuln in data.get("vulnerabilities", {}).items():
                severity = vuln.get("severity", "low").upper()
                if severity == "CRITICAL":
                    severity = "CRITICAL"
                elif severity == "HIGH":
                    severity = "HIGH"
                else:
                    severity = "MEDIUM"

                vulns.append({
                    "package": vuln.get("name", ""),
                    "version": vuln.get("version", ""),
                    "id": vuln_id,
                    "severity": severity,
                    "recommendation": "Update to patched version"
                })
        except:
            pass

        return vulns

    def _pip_audit(self, repo_path: Path) -> None:
        """Audit pip dependencies"""
        requirements = repo_path / "requirements.txt"
        if not requirements.exists():
            return

        pip = find_tool("pip")
        if not pip:
            return

        print("   ├─ Pip audit...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [pip, "audit", "--desc"],
                capture_output=True,
                text=True,
                timeout=300
            )

            vulns = self._parse_pip_audit(result.stdout)
            print(f"✅ ({len(vulns)} vulnerabilities)")

            for vuln in vulns:
                self.findings.append({
                    "title": f"Vulnerable Python package: {vuln['package']}",
                    "severity": vuln["severity"],
                    "category": "dependency",
                    "evidence": {
                        "package": vuln["package"],
                        "vulnerability": vuln["id"]
                    },
                    "recommendation": f"Update {vuln['package']} to patched version"
                })

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_pip_audit(self, output: str) -> List[Dict]:
        """Parse pip audit output"""
        vulns = []
        lines = output.split("\n")
        for i, line in enumerate(lines):
            if "VULN" in line or "Found" in line:
                # pip audit format: Package X has Y vulnerability
                match = re.search(r"([a-z0-9\-_]+)\s+has\s+(\d+)", line, re.IGNORECASE)
                if match:
                    vulns.append({
                        "package": match.group(1),
                        "id": f"pip-vuln-{i}",
                        "severity": "HIGH",
                        "recommendation": "Update package"
                    })

        return vulns

    def _trivy_scan(self, repo_path: Path) -> None:
        """Scan container images and dependencies with trivy"""
        trivy = find_tool("trivy")
        if not trivy:
            return

        print("   ├─ Trivy scanning...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [trivy, "fs", "--json", str(repo_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            vulns = self._parse_trivy(result.stdout)
            print(f"✅ ({len(vulns)} vulnerabilities)")

            for vuln in vulns:
                self.findings.append({
                    "title": f"Container vulnerability: {vuln['id']}",
                    "severity": vuln["severity"],
                    "category": "container",
                    "evidence": {
                        "cve": vuln["id"],
                        "package": vuln.get("package", "")
                    },
                    "recommendation": "Update or patch container"
                })

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_trivy(self, output: str) -> List[Dict]:
        """Parse trivy JSON output"""
        vulns = []
        try:
            data = json.loads(output)
            for result in data.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    severity = vuln.get("Severity", "MEDIUM")
                    vulns.append({
                        "id": vuln.get("VulnerabilityID", ""),
                        "severity": severity,
                        "package": vuln.get("PkgName", ""),
                        "recommendation": "Update package"
                    })
        except:
            pass

        return vulns


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run code analysis phase")
    parser.add_argument("repo", nargs="?", default=".", help="Repository path")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=3)
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    analyzer = CodeAnalysisPhase("local", level=args.level)
    findings = analyzer.run(args.repo)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(findings, f, indent=2)
        print(f"\n✅ Findings saved to {args.output}")

    print(f"\n📊 Total findings: {len(findings)}")


if __name__ == "__main__":
    main()
