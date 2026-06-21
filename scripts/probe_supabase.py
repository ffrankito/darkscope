#!/usr/bin/env python3
"""
Automated Supabase RLS and REST API security testing.
Probes for:
- Anonymous access to private tables
- Improper DELETE/UPDATE/INSERT on anon role
- JWT inspection
- CORS misconfiguration
"""

import json
import sys
import base64
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import requests
from pathlib import Path

class SupabaseProber:
    """Test Supabase project RLS and API security"""

    def __init__(self, project_ref: str, anon_key: str, verify_ssl: bool = True):
        self.project_ref = project_ref
        self.anon_key = anon_key
        self.base_url = f"https://{project_ref}.supabase.co"
        self.rest_url = f"{self.base_url}/rest/v1"
        self.verify_ssl = verify_ssl
        self.headers = {
            "apikey": anon_key,
            "Content-Type": "application/json",
        }
        self.findings = []

    def test_all_tables(self) -> List[Dict]:
        """Discover and test all tables"""
        print(f"🔍 Discovering tables in {self.project_ref}...")

        tables = self._get_tables()
        if not tables:
            print("❌ Could not discover tables. Check API key permissions.")
            return []

        print(f"✅ Found {len(tables)} tables\n")

        for table in tables:
            print(f"🧪 Testing table: {table}")
            self._test_table_rls(table)

        return self.findings

    def _get_tables(self) -> List[str]:
        """Get list of tables from REST API"""
        try:
            response = requests.get(
                f"{self.rest_url}/?apikey={self.anon_key}",
                headers={"apikey": self.anon_key},
                verify=self.verify_ssl,
                timeout=10
            )

            if response.status_code == 200:
                # Supabase lists available tables
                return [t for t in response.json() if isinstance(t, str)]
        except Exception as e:
            print(f"⚠️  Error discovering tables: {e}")

        # Fallback: test common table names
        return self._test_common_tables()

    def _test_common_tables(self) -> List[str]:
        """Test for common table names"""
        common = [
            "clients", "patients", "appointments", "consultations",
            "users", "staff", "products", "services", "orders",
            "hospitalizations", "procedures", "consent_documents",
            "grooming_sessions", "settings", "charges"
        ]

        found = []
        for table in common:
            try:
                response = requests.head(
                    f"{self.rest_url}/{table}",
                    headers=self.headers,
                    verify=self.verify_ssl,
                    timeout=5
                )
                if response.status_code < 404:
                    found.append(table)
            except:
                pass

        return found

    def _test_table_rls(self, table: str) -> None:
        """Test SELECT/INSERT/UPDATE/DELETE on a table"""
        operations = [
            ("SELECT", "get", lambda: self._test_select(table)),
            ("INSERT", "post", lambda: self._test_insert(table)),
            ("UPDATE", "patch", lambda: self._test_update(table)),
            ("DELETE", "delete", lambda: self._test_delete(table)),
        ]

        for op_name, method, test_func in operations:
            result = test_func()
            status = result['status']
            accessible = result['accessible']

            # Log findings
            if accessible:
                severity = "CRITICAL" if op_name in ["SELECT", "INSERT", "UPDATE", "DELETE"] else "HIGH"
                finding = {
                    "table": table,
                    "operation": op_name,
                    "severity": severity,
                    "evidence": result,
                    "recommendation": self._get_remediation(table, op_name)
                }
                self.findings.append(finding)
                print(f"  ❌ {op_name:6} {status:3} - ACCESSIBLE (anon can {op_name})")
            else:
                print(f"  ✅ {op_name:6} {status:3} - Blocked (expected)")

    def _test_select(self, table: str) -> Dict[str, Any]:
        """Test SELECT access"""
        try:
            response = requests.get(
                f"{self.rest_url}/{table}?select=count",
                headers=self.headers,
                params={"Prefer": "count=exact"},
                verify=self.verify_ssl,
                timeout=10
            )

            accessible = response.status_code == 200
            row_count = None

            if accessible:
                try:
                    row_count = int(response.headers.get("Content-Range", "0/*").split("/")[1])
                except:
                    row_count = "unknown"

            return {
                "status": response.status_code,
                "accessible": accessible,
                "row_count": row_count,
                "response_preview": response.text[:100] if accessible else None
            }
        except Exception as e:
            return {
                "status": 0,
                "accessible": False,
                "error": str(e)
            }

    def _test_insert(self, table: str) -> Dict[str, Any]:
        """Test INSERT with invalid body (no data writes)"""
        try:
            response = requests.post(
                f"{self.rest_url}/{table}",
                headers=self.headers,
                json={"__invalid_field__": None},
                verify=self.verify_ssl,
                timeout=10
            )

            # 401/403 = good (blocked by RLS)
            # 400 = bad (validation error, RLS didn't block)
            # 201 = critical (actually inserted)
            accessible = response.status_code not in [401, 403]

            return {
                "status": response.status_code,
                "accessible": accessible,
                "reason": "RLS blocked" if not accessible else "RLS did not block insert attempt"
            }
        except Exception as e:
            return {
                "status": 0,
                "accessible": False,
                "error": str(e)
            }

    def _test_update(self, table: str) -> Dict[str, Any]:
        """Test UPDATE with nonexistent ID (no data writes)"""
        try:
            response = requests.patch(
                f"{self.rest_url}/{table}?id=eq.999999999",
                headers=self.headers,
                json={"id": 999999999},
                verify=self.verify_ssl,
                timeout=10
            )

            accessible = response.status_code not in [401, 403]

            return {
                "status": response.status_code,
                "accessible": accessible,
                "reason": "RLS blocked" if not accessible else "RLS did not block update attempt"
            }
        except Exception as e:
            return {
                "status": 0,
                "accessible": False,
                "error": str(e)
            }

    def _test_delete(self, table: str) -> Dict[str, Any]:
        """Test DELETE with nonexistent ID (no data writes)"""
        try:
            response = requests.delete(
                f"{self.rest_url}/{table}?id=eq.999999999",
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=10
            )

            accessible = response.status_code not in [401, 403]

            return {
                "status": response.status_code,
                "accessible": accessible,
                "reason": "RLS blocked" if not accessible else "RLS did not block delete attempt"
            }
        except Exception as e:
            return {
                "status": 0,
                "accessible": False,
                "error": str(e)
            }

    def inspect_jwt(self, token: str) -> Dict[str, Any]:
        """Decode and inspect JWT claims"""
        try:
            # JWT format: header.payload.signature
            parts = token.split(".")
            if len(parts) != 3:
                return {"error": "Invalid JWT format"}

            # Decode payload (add padding if needed)
            payload = parts[1]
            payload += "=" * (4 - len(payload) % 4)

            decoded = json.loads(base64.urlsafe_b64decode(payload))

            # Check for suspicious claims
            issues = []
            if "user_metadata" in decoded and decoded["user_metadata"]:
                if any(key in decoded["user_metadata"] for key in ["password", "ssn", "credit_card"]):
                    issues.append("Sensitive data in user_metadata")

            if decoded.get("exp"):
                import time
                if decoded["exp"] - time.time() > 2592000:  # 30 days
                    issues.append("Very long token expiration")

            return {
                "decoded": decoded,
                "issues": issues,
                "safe": len(issues) == 0
            }
        except Exception as e:
            return {"error": str(e)}

    def test_cors(self, origin: str = "https://attacker.example.com") -> Dict[str, Any]:
        """Test CORS misconfiguration"""
        try:
            response = requests.get(
                f"{self.rest_url}/",
                headers={
                    "apikey": self.anon_key,
                    "Origin": origin
                },
                verify=self.verify_ssl,
                timeout=10
            )

            allow_origin = response.headers.get("Access-Control-Allow-Origin", "not set")
            allow_credentials = response.headers.get("Access-Control-Allow-Credentials", "not set")

            misconfigured = allow_origin == "*" or (allow_origin == origin and allow_credentials == "true")

            return {
                "allow_origin": allow_origin,
                "allow_credentials": allow_credentials,
                "misconfigured": misconfigured,
                "severity": "CRITICAL" if misconfigured else "OK"
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate JSON report"""
        report = {
            "project_ref": self.project_ref,
            "findings": self.findings,
            "summary": {
                "total_findings": len(self.findings),
                "critical": len([f for f in self.findings if f["severity"] == "CRITICAL"]),
                "high": len([f for f in self.findings if f["severity"] == "HIGH"]),
            }
        }

        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
            return str(output_file)

        return json.dumps(report, indent=2)

    @staticmethod
    def _get_remediation(table: str, operation: str) -> str:
        """Get remediation advice"""
        if operation == "SELECT":
            return f"CREATE POLICY {table}_read ON {table} FOR SELECT USING (auth.uid() = user_id);"
        elif operation == "INSERT":
            return f"CREATE POLICY {table}_write ON {table} FOR INSERT WITH CHECK (auth.uid() = user_id);"
        elif operation == "UPDATE":
            return f"CREATE POLICY {table}_update ON {table} FOR UPDATE USING (auth.uid() = user_id);"
        elif operation == "DELETE":
            return f"CREATE POLICY {table}_delete ON {table} FOR DELETE USING (auth.uid() = user_id);"
        return "Review RLS policies"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Probe Supabase RLS and REST API security.")
    parser.add_argument("--project-ref", required=True, help="Supabase project ref")
    parser.add_argument("--anon-key", required=True, help="Supabase anon API key")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL verification (dev only)")
    parser.add_argument("--jwt-token", help="JWT token to inspect")
    parser.add_argument("--test-cors", action="store_true", help="Test CORS configuration")
    args = parser.parse_args()

    prober = SupabaseProber(args.project_ref, args.anon_key, verify_ssl=not args.no_verify_ssl)

    print(f"🔍 Probing Supabase project: {args.project_ref}\n")

    # Test RLS
    prober.test_all_tables()

    # Test JWT if provided
    if args.jwt_token:
        print("\n🔐 Inspecting JWT...")
        jwt_result = prober.inspect_jwt(args.jwt_token)
        if "decoded" in jwt_result:
            print(json.dumps(jwt_result["decoded"], indent=2))
            if jwt_result.get("issues"):
                print(f"⚠️  Issues: {', '.join(jwt_result['issues'])}")

    # Test CORS
    if args.test_cors:
        print("\n🌐 Testing CORS...")
        cors_result = prober.test_cors()
        print(json.dumps(cors_result, indent=2))

    # Generate report
    print("\n📝 Generating report...")
    report_file = args.output or Path("supabase_probe_report.json")
    prober.generate_report(Path(report_file))
    print(f"✅ Report saved to: {report_file}")

    # Exit with error if critical findings
    if any(f["severity"] == "CRITICAL" for f in prober.findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
