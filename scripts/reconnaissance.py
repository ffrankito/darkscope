#!/usr/bin/env python3
"""
Reconnaissance Phase: Network scanning, web fingerprinting, SSL/TLS analysis
Uses: nmap, whatweb, wafw00f, sslscan, curl
"""

import json
import subprocess
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from urllib.parse import urlparse

from check_tools import find_tool


class ReconnaissancePhase:
    """Execute reconnaissance probes"""

    def __init__(self, target: str, level: int = 2, timeout: int = 600):
        self.target = target
        self.level = level
        self.timeout = timeout
        self.findings = []
        self.parsed = urlparse(target)
        self.host = self.parsed.hostname or target.split("/")[0]

    def run(self) -> List[Dict[str, Any]]:
        """Execute all reconnaissance probes"""
        print(f"\n🔍 Reconnaissance Phase (Level {self.level})")
        print(f"   Target: {self.target}\n")

        # Phase 0: HTTP Headers
        self._test_headers()

        # Phase 1+: Framework detection
        if self.level >= 1:
            self._whatweb_scan()
            self._waf_detection()

        # Phase 1+: Network scanning
        if self.level >= 1:
            self._nmap_scan()

        # Phase 1+: SSL/TLS analysis
        if self.level >= 1 and self.target.startswith("https://"):
            self._sslscan()

        return self.findings

    def _test_headers(self) -> None:
        """Test basic HTTP headers"""
        print("   ├─ HTTP Headers...", end=" ", flush=True)
        try:
            import requests
            response = requests.head(self.target, timeout=10, allow_redirects=True)

            # Check for security headers
            headers = response.headers
            missing_headers = []

            security_headers = {
                "X-Frame-Options": "Clickjacking protection",
                "X-Content-Type-Options": "MIME type sniffing",
                "Strict-Transport-Security": "HSTS enforcement",
                "Content-Security-Policy": "XSS protection",
            }

            for header, description in security_headers.items():
                if header not in headers:
                    missing_headers.append((header, description))

            if missing_headers:
                print(f"❌ ({len(missing_headers)} missing)")
                for header, desc in missing_headers:
                    self.findings.append({
                        "title": f"Missing security header: {header}",
                        "severity": "MEDIUM",
                        "category": "headers",
                        "evidence": {"header": header, "description": desc},
                        "recommendation": f"Add {header} header to HTTP responses"
                    })
            else:
                print("✅")

            # Check CORS
            if "Access-Control-Allow-Origin" in headers:
                cors_origin = headers["Access-Control-Allow-Origin"]
                if cors_origin == "*":
                    print("   ├─ CORS...", end=" ", flush=True)
                    print("❌ (wildcard)")
                    self.findings.append({
                        "title": "CORS misconfiguration: wildcard allowed",
                        "severity": "HIGH",
                        "category": "cors",
                        "evidence": {"CORS": cors_origin},
                        "recommendation": "Restrict CORS to specific origins"
                    })

        except Exception as e:
            print(f"⚠️  ({str(e)[:30]})")

    def _whatweb_scan(self) -> None:
        """Detect web technologies using whatweb"""
        whatweb = find_tool("whatweb")
        if not whatweb:
            return

        print("   ├─ Technology fingerprinting...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [whatweb, "-q", "--headers", self.target],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                techs = self._parse_whatweb(result.stdout)
                print(f"✅ ({len(techs)} detected)")
                # Log technologies found
            else:
                print("⚠️")
        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_whatweb(self, output: str) -> List[str]:
        """Parse whatweb output"""
        techs = []
        for line in output.split("\n"):
            if "[" in line and "]" in line:
                match = re.search(r"\[([^\]]+)\]", line)
                if match:
                    techs.append(match.group(1))
        return techs

    def _waf_detection(self) -> None:
        """Detect WAF using wafw00f"""
        wafw00f = find_tool("wafw00f")
        if not wafw00f:
            return

        print("   ├─ WAF detection...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [wafw00f, "-a", self.target],
                capture_output=True,
                text=True,
                timeout=120
            )

            if "GenericDetection" not in result.stdout:
                # WAF detected
                print("✅ (detected)")
                self.findings.append({
                    "title": "Web Application Firewall detected",
                    "severity": "INFO",
                    "category": "infrastructure",
                    "evidence": {"output": result.stdout[:200]},
                    "recommendation": "Ensure WAF rules are appropriate"
                })
            else:
                print("✅ (not detected)")
        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _nmap_scan(self) -> None:
        """Network reconnaissance using nmap"""
        nmap = find_tool("nmap")
        if not nmap:
            return

        print("   ├─ Network scanning...", end=" ", flush=True)
        try:
            # Only scan common web ports
            result = subprocess.run(
                [nmap, "-sV", "-Pn", "-p", "80,443,8080,8443", "--open", self.host],
                capture_output=True,
                text=True,
                timeout=300
            )

            open_ports = self._parse_nmap(result.stdout)
            print(f"✅ ({len(open_ports)} ports)")

            for port, service in open_ports:
                # Log open ports found
                pass

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_nmap(self, output: str) -> List[tuple]:
        """Parse nmap output"""
        ports = []
        for line in output.split("\n"):
            if "open" in line:
                match = re.search(r"(\d+)/tcp\s+open\s+(\S+)", line)
                if match:
                    ports.append((match.group(1), match.group(2)))
        return ports

    def _sslscan(self) -> None:
        """Analyze SSL/TLS configuration using sslscan"""
        sslscan = find_tool("sslscan")
        if not sslscan:
            return

        print("   ├─ SSL/TLS analysis...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [sslscan, "--quiet", self.host],
                capture_output=True,
                text=True,
                timeout=120
            )

            issues = self._parse_ssl(result.stdout)
            if issues:
                print(f"❌ ({len(issues)} issues)")
                for issue in issues:
                    self.findings.append({
                        "title": f"SSL/TLS weakness: {issue}",
                        "severity": "MEDIUM",
                        "category": "ssl",
                        "evidence": {"issue": issue},
                        "recommendation": "Update SSL/TLS configuration"
                    })
            else:
                print("✅ (secure)")

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_ssl(self, output: str) -> List[str]:
        """Parse SSL weaknesses"""
        issues = []
        if "weak" in output.lower() or "deprecated" in output.lower():
            if "SSLv2" in output or "SSLv3" in output:
                issues.append("Deprecated SSL version")
            if "RC4" in output:
                issues.append("Weak cipher: RC4")
            if "MD5" in output:
                issues.append("Weak hash algorithm: MD5")
        return issues


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run reconnaissance phase")
    parser.add_argument("target", help="Target URL")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2)
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    recon = ReconnaissancePhase(args.target, level=args.level)
    findings = recon.run()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(findings, f, indent=2)
        print(f"\n✅ Findings saved to {args.output}")

    print(f"\n📊 Total findings: {len(findings)}")


if __name__ == "__main__":
    main()
