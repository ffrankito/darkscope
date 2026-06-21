#!/usr/bin/env python3
"""
Request explicit user authorization before running security assessments.
This is a critical safety feature - prevents accidental or unauthorized testing.
"""

import sys
from datetime import datetime
from pathlib import Path


class AuthorizationManager:
    """Manage authorization for security assessments"""

    def __init__(self, target: str, level: int, env: str = "production"):
        self.target = target
        self.level = level
        self.env = env
        self.timestamp = datetime.now().isoformat()

    def level_description(self) -> str:
        descriptions = {
            0: "Passive orientation (quiet, no active probes)",
            1: "Safe production baseline (low-noise checks)",
            2: "Standard authorized production (medium intensity)",
            3: "Deep controlled testing (aggressive probes)",
            4: "Aggressive lab/staging (very high intensity)",
            5: "Enterprise assurance (full automation)",
        }
        return descriptions.get(self.level, "Unknown")

    def request_confirmation(self, auto_approved: bool = False) -> bool:
        """Request explicit authorization before testing"""

        # If auto_approved (e.g., from CI), still log it
        if auto_approved:
            print("ℹ️  Authorization auto-approved (CI/CD context detected)")
            self._log_authorization(approved=True, method="auto")
            return True

        # Display authorization prompt
        self._display_prompt()

        # Get user input
        response = input("\n➜ Type 'I AUTHORIZE TESTING' to proceed: ").strip()

        if response != "I AUTHORIZE TESTING":
            print("\n❌ Authorization DENIED.")
            self._log_authorization(approved=False, method="denied")
            sys.exit(1)

        print("\n✅ Authorization CONFIRMED. Assessment starting...\n")
        self._log_authorization(approved=True, method="interactive")
        return True

    def _display_prompt(self) -> None:
        """Display the authorization prompt"""
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║                  ⚠️  AUTHORIZATION REQUIRED  ⚠️                ║
╚════════════════════════════════════════════════════════════════╝

Target:       {self.target}
Level:        {self.level} ({self.level_description()})
Environment:  {self.env}
Timestamp:    {self.timestamp}

┌────────────────────────────────────────────────────────────────┐
│ You are about to run an AUTHORIZED SECURITY ASSESSMENT.        │
│ This tool probes for real security weaknesses.                 │
│                                                                │
│ By proceeding, you confirm that:                              │
│                                                                │
│ ✓ You own this system OR have explicit WRITTEN permission    │
│ ✓ You understand this is an OFFENSIVE security tool           │
│ ✓ You are prepared to remediate all findings                  │
│ ✓ Relevant teams (security, product, ops) have been notified  │
│ ✓ You accept responsibility for all actions taken             │
│                                                                │
│ UNAUTHORIZED TESTING IS ILLEGAL.                              │
│ DarkScope logs all activity.                                  │
│ Use responsibly.                                              │
└────────────────────────────────────────────────────────────────┘
        """)

    def _log_authorization(self, approved: bool, method: str) -> None:
        """Log authorization decision"""
        log_dir = Path("./darkscope_auth_logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        status = "APPROVED" if approved else "DENIED"
        content = f"""
DarkScope Authorization Log
{'=' * 50}

Status:       {status}
Method:       {method}
Target:       {self.target}
Level:        {self.level} ({self.level_description()})
Environment:  {self.env}
Timestamp:    {self.timestamp}
PID:          {sys.argv[0] if sys.argv else 'unknown'}

User:         {self._get_user()}
Hostname:     {self._get_hostname()}

Notes:
- This log proves you authorized testing for audit/compliance
- Keep these logs for at least 30 days
- If assessment was unauthorized, report to your security team immediately
"""

        with open(log_file, "w") as f:
            f.write(content)

        print(f"📝 Authorization logged to: {log_file}")

    @staticmethod
    def _get_user() -> str:
        """Get current user"""
        import getpass
        try:
            return getpass.getuser()
        except:
            return "unknown"

    @staticmethod
    def _get_hostname() -> str:
        """Get system hostname"""
        import socket
        try:
            return socket.gethostname()
        except:
            return "unknown"


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Request authorization for security assessment.")
    parser.add_argument("target", help="Target URL or IP to assess")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2, help="Assessment level (0-5)")
    parser.add_argument("--env", choices=["production", "staging", "lab"], default="production", help="Environment")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve (CI/CD only)")
    args = parser.parse_args()

    manager = AuthorizationManager(args.target, args.level, args.env)
    authorized = manager.request_confirmation(auto_approved=args.auto_approve)

    if authorized:
        print("✅ Ready to proceed with assessment.")
        return 0
    else:
        print("❌ Assessment cancelled.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
