#!/usr/bin/env python3
"""
Discovery Phase: Route and endpoint enumeration
Uses: feroxbuster, ffuf, katana, JavaScript analysis
"""

import json
import subprocess
import re
from typing import List, Dict, Any, Set
from urllib.parse import urljoin, urlparse
import requests

from check_tools import find_tool


class DiscoveryPhase:
    """Discover routes and endpoints"""

    def __init__(self, target: str, level: int = 2, timeout: int = 900):
        self.target = target
        self.level = level
        self.timeout = timeout
        self.findings = []
        self.discovered_routes = set()

    def run(self) -> List[Dict[str, Any]]:
        """Execute route discovery"""
        print(f"\n🔎 Discovery Phase (Level {self.level})")
        print(f"   Target: {self.target}\n")

        # Level 0: Manual routes only
        self._test_manual_routes()

        # Level 1+: Basic discovery
        if self.level >= 1:
            self._ffuf_discovery()

        # Level 2+: Aggressive discovery
        if self.level >= 2:
            self._feroxbuster_discovery()
            self._javascript_analysis()

        # Level 3+: Full enumeration
        if self.level >= 3:
            self._katana_discovery()

        return self.findings

    def _test_manual_routes(self) -> None:
        """Test common routes manually"""
        print("   ├─ Manual routes...", end=" ", flush=True)

        common_routes = [
            "/", "/login", "/admin", "/dashboard", "/api", "/api/health",
            "/robots.txt", "/sitemap.xml", "/.well-known/security.json",
            "/config.js", "/assets/", "/public/", "/static/",
            "/api/v1", "/api/v2", "/graphql", "/api/users", "/api/posts"
        ]

        found = 0
        for route in common_routes:
            url = urljoin(self.target.rstrip("/") + "/", route.lstrip("/"))
            try:
                response = requests.head(url, timeout=5, allow_redirects=False)
                if response.status_code < 404:
                    self.discovered_routes.add(route)
                    found += 1
            except:
                pass

        print(f"✅ ({found} found)")

    def _ffuf_discovery(self) -> None:
        """Fast URL fuzzing with ffuf"""
        ffuf = find_tool("ffuf")
        if not ffuf:
            return

        print("   ├─ Common wordlist fuzzing...", end=" ", flush=True)
        try:
            wordlist = "/usr/share/wordlists/dirb/common.txt"
            result = subprocess.run(
                [ffuf, "-u", self.target.rstrip("/") + "/FUZZ", "-w", wordlist,
                 "-mc", "200,204,301,302,307,401,403", "-rate", "10",
                 "-t", "5", "-ac", "-s"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            routes = self._parse_ffuf(result.stdout)
            found = len(routes)
            print(f"✅ ({found} found)")

            for route in routes:
                self.discovered_routes.add(route)

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_ffuf(self, output: str) -> List[str]:
        """Parse ffuf output"""
        routes = []
        for line in output.split("\n"):
            # ffuf format: url [status code, size]
            match = re.search(r"\[Status: \d+, Size: \d+\]\s+(.+?)(?:\s+\[|$)", line)
            if match:
                route = match.group(1).strip()
                if route:
                    routes.append(route)
        return routes

    def _feroxbuster_discovery(self) -> None:
        """Deep directory discovery with feroxbuster"""
        feroxbuster = find_tool("feroxbuster")
        if not feroxbuster:
            return

        print("   ├─ Deep directory discovery...", end=" ", flush=True)
        try:
            wordlist = "/usr/share/wordlists/dirb/common.txt"
            result = subprocess.run(
                [feroxbuster, "-u", self.target, "-w", wordlist,
                 "-x", "js,json,txt,xml,html", "--rate-limit", "10",
                 "-t", "5", "-q", "--auto-bail"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            routes = self._parse_feroxbuster(result.stdout)
            found = len(routes)
            print(f"✅ ({found} found)")

            for route in routes:
                self.discovered_routes.add(route)

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _parse_feroxbuster(self, output: str) -> List[str]:
        """Parse feroxbuster output"""
        routes = []
        for line in output.split("\n"):
            # feroxbuster format: GET /path [Status: 200, Size: 1234]
            match = re.search(r"(GET|POST|PUT|DELETE)\s+([^\s]+)\s+\[Status", line)
            if match:
                route = match.group(2)
                routes.append(route)
        return routes

    def _javascript_analysis(self) -> None:
        """Extract routes from JavaScript files"""
        print("   ├─ JavaScript analysis...", end=" ", flush=True)

        try:
            response = requests.get(self.target, timeout=10)
            html = response.text

            # Find script tags
            scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)

            # Extract route patterns
            routes = re.findall(
                r'["\']\/(?:[a-zA-Z0-9\-_\/]*)["\']',
                html
            )

            found = len(set(routes))
            print(f"✅ ({found} found)")

            for route in routes:
                route_clean = route.strip('"\'')
                self.discovered_routes.add(route_clean)

            # Check for API endpoints
            api_routes = re.findall(
                r'["\']\/api\/[a-zA-Z0-9\-_\/]*["\']',
                html
            )

            if api_routes:
                self.findings.append({
                    "title": f"API endpoints discoverable in JavaScript",
                    "severity": "LOW",
                    "category": "disclosure",
                    "evidence": {"routes": list(set(api_routes))[:5]},
                    "recommendation": "Minimize route exposure in client-side code"
                })

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")

    def _katana_discovery(self) -> None:
        """Full crawl using Katana"""
        katana = find_tool("katana")
        if not katana:
            return

        print("   ├─ Full crawl (katana)...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [katana, "-u", self.target, "-d", "2", "-silent"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            routes = result.stdout.strip().split("\n")
            found = len([r for r in routes if r])
            print(f"✅ ({found} found)")

            for route in routes:
                if route:
                    self.discovered_routes.add(route)

        except Exception as e:
            print(f"⚠️  ({str(e)[:20]})")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run discovery phase")
    parser.add_argument("target", help="Target URL")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2)
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    discovery = DiscoveryPhase(args.target, level=args.level)
    findings = discovery.run()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(findings, f, indent=2)
        print(f"\n✅ Findings saved to {args.output}")

    print(f"\n📊 Total findings: {len(findings)}")


if __name__ == "__main__":
    main()
