#!/usr/bin/env python3
"""
SQL Testing Phase: SQL injection and database security testing
Uses: sqlmap, manual queries
"""

import json
import subprocess
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
import requests

from check_tools import find_tool


class SQLTesting:
    """Execute SQL injection testing"""

    def __init__(self, target: str, level: int = 3, timeout: int = 1200):
        self.target = target
        self.level = level
        self.timeout = timeout
        self.findings = []

    def run(self) -> List[Dict[str, Any]]:
        """Execute SQL testing"""
        print(f"\n💾 SQL Testing Phase (Level {self.level})")
        print(f"   Target: {self.target}\n")

        # Level 3+: Manual parameter testing
        if self.level >= 3:
            self._manual_sqli_test()

        # Level 4+: Aggressive sqlmap testing
        if self.level >= 4:
            self._sqlmap_testing()

        return self.findings

    def _manual_sqli_test(self) -> None:
        """Manual SQL injection testing on common parameters"""
        print("   ├─ Manual SQLi testing...", end=" ", flush=True)

        common_params = ["id", "user", "search", "q", "page", "sort", "category"]
        payloads = ["'", "' OR '1'='1", "' OR 1=1--", "'; DROP TABLE users--"]

        vulnerable = []
        for param in common_params:
            for payload in payloads:
                url = f"{self.target.rstrip('/')}?{param}={payload}"
                try:
                    response = requests.get(url, timeout=5)

                    # Check for SQL error patterns
                    if self._has_sql_error(response.text):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "error": self._extract_sql_error(response.text)
                        })
                        break  # Found for this param, move to next

                except:
                    pass

        if vulnerable:
            print(f"❌ ({len(vulnerable)} parameters)")
            for vuln in vulnerable:
                self.findings.append({
                    "title": f"SQL injection in parameter: {vuln['param']}",
                    "severity": "CRITICAL",
                    "category": "sql_injection",
                    "evidence": {
                        "parameter": vuln["param"],
                        "payload": vuln["payload"],
                        "error": vuln.get("error", "")[:100]
                    },
                    "recommendation": "Use prepared statements and parameterized queries"
                })
        else:
            print("✅")

    @staticmethod
    def _has_sql_error(response: str) -> bool:
        """Check if response contains SQL error"""
        error_patterns = [
            r"SQL syntax",
            r"MySQL error",
            r"PostgreSQL error",
            r"syntax error",
            r"database error",
            r"SQL Server",
            r"ORA-\d+",
            r"JDBC",
            r"Exception",
            r"Unknown column"
        ]

        for pattern in error_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def _extract_sql_error(response: str) -> str:
        """Extract SQL error message"""
        match = re.search(r"(SQL\s+\w+.*?)(?:<|$)", response, re.IGNORECASE)
        if match:
            return match.group(1)[:100]
        return "SQL error detected"

    def _sqlmap_testing(self) -> None:
        """Aggressive SQLmap testing"""
        sqlmap = find_tool("sqlmap")
        if not sqlmap:
            return

        print("   ├─ SQLmap testing...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [sqlmap, "-u", self.target, "--batch", "--level", "2", "--risk", "2",
                 "--smart", "-v", "0"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            vulns = self._parse_sqlmap(result.stdout)
            print(f"✅ ({len(vulns)} databases)")

            if vulns:
                for vuln in vulns:
                    self.findings.append({
                        "title": f"SQL injection confirmed: {vuln['type']}",
                        "severity": "CRITICAL",
                        "category": "sql_injection",
                        "evidence": {
                            "technique": vuln["type"],
                            "database": vuln.get("database", "Unknown"),
                            "parameter": vuln.get("parameter", "")
                        },
                        "recommendation": "Use parameterized queries, ORM, stored procedures"
                    })

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_sqlmap(self, output: str) -> List[Dict]:
        """Parse sqlmap output"""
        vulns = []
        lines = output.split("\n")

        for i, line in enumerate(lines):
            if "vulnerability found" in line.lower():
                # Extract injection type
                match = re.search(r"(\w+\s+injection)", line, re.IGNORECASE)
                if match:
                    vuln_type = match.group(1)
                    vulns.append({
                        "type": vuln_type,
                        "parameter": "",
                        "database": ""
                    })

            # Extract database info
            if "database:" in line.lower() or "dbms:" in line.lower():
                match = re.search(r":\s*(.+?)(?:$|\s+)", line)
                if match and vulns:
                    vulns[-1]["database"] = match.group(1)

        return vulns


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run SQL testing phase")
    parser.add_argument("target", help="Target URL with vulnerable parameter")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=3)
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    tester = SQLTesting(args.target, level=args.level)
    findings = tester.run()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(findings, f, indent=2)
        print(f"\n✅ Findings saved to {args.output}")

    print(f"\n📊 Total findings: {len(findings)}")


if __name__ == "__main__":
    main()
