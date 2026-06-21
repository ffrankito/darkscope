#!/usr/bin/env python3
"""
Example DarkScope plugin: Custom security checks for NeoVet CRM.

This plugin demonstrates how to create custom checks for your organization.
Copy and modify this file to add your own security probes.
"""

import requests
from typing import List, Dict, Any
from pathlib import Path
import sys

# Import plugin base class
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from plugin_manager import DarkScopePlugin


class NeoVetCrmPlugin(DarkScopePlugin):
    """Custom security checks for NeoVet CRM"""

    name = "NeoVet CRM Custom Checks"
    description = "Veterinary clinic CRM security checks (NeoVet-specific)"
    level_required = 2  # Runs on Level 2+
    version = "1.0.0"

    def run(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute NeoVet-specific security checks"""
        findings = []

        # Check 1: Verify HIPAA-like protections
        print("     - Checking HIPAA-like protections...", end=' ', flush=True)
        hipaa_findings = self._check_patient_data_exposure(target)
        findings.extend(hipaa_findings)
        print(f"({len(hipaa_findings)} findings)")

        # Check 2: Verify role-based access control
        print("     - Checking RBAC...", end=' ', flush=True)
        rbac_findings = self._check_role_separation(target)
        findings.extend(rbac_findings)
        print(f"({len(rbac_findings)} findings)")

        # Check 3: Verify consent documents are protected
        print("     - Checking consent doc protection...", end=' ', flush=True)
        consent_findings = self._check_consent_protection(target)
        findings.extend(consent_findings)
        print(f"({len(consent_findings)} findings)")

        return findings

    def _check_patient_data_exposure(self, target: str) -> List[Dict[str, Any]]:
        """Check if patient data is exposed via public APIs"""
        findings = []

        tables = ['patients', 'consultations', 'hospitalizations', 'procedures']

        for table in tables:
            try:
                # Attempt to access table as anonymous
                response = requests.get(
                    f"{target}/api/bot/patients",  # Assuming bot API
                    timeout=10
                )

                if response.status_code == 200:
                    findings.append({
                        'title': f'NeoVet: Patient data accessible via API',
                        'severity': 'CRITICAL',
                        'table': table,
                        'evidence': {
                            'endpoint': f"{target}/api/bot/{table}",
                            'status': response.status_code,
                            'accessible': True
                        },
                        'recommendation': 'Implement authentication on /api/bot/* endpoints or restrict to authenticated users only'
                    })
            except:
                pass

        return findings

    def _check_role_separation(self, target: str) -> List[Dict[str, Any]]:
        """Check if roles have proper separation of duties"""
        findings = []

        # Example: Check that groomer cannot access financial data
        # (This would need valid credentials to test properly)

        findings.append({
            'title': 'NeoVet: RBAC test requires authenticated user',
            'severity': 'INFO',
            'evidence': {'note': 'Requires valid credentials to test'},
            'recommendation': 'Manual testing needed with test accounts for each role'
        })

        return findings

    def _check_consent_protection(self, target: str) -> List[Dict[str, Any]]:
        """Check if consent documents are properly protected"""
        findings = []

        # Check if /api/consent-documents is accessible without auth
        try:
            response = requests.get(
                f"{target}/api/consent-documents",
                timeout=10
            )

            if response.status_code == 200:
                findings.append({
                    'title': 'NeoVet: Consent documents accessible without authentication',
                    'severity': 'CRITICAL',
                    'evidence': {
                        'endpoint': f"{target}/api/consent-documents",
                        'status': response.status_code
                    },
                    'recommendation': 'Restrict consent document endpoints to authenticated, authorized users only'
                })
        except:
            pass

        return findings


class VeterinaryDataProtectionPlugin(DarkScopePlugin):
    """Additional plugin for veterinary-specific data protection"""

    name = "Veterinary Data Protection"
    description = "Checks for proper protection of sensitive veterinary records"
    level_required = 3  # Runs on Level 3+
    version = "1.0.0"

    def run(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Check veterinary-specific protections"""
        findings = []

        # Check: Verify sensitive breed/breed-specific conditions are protected
        # (Some breeds have medical privacy concerns)

        findings.append({
            'title': 'Veterinary Data Protection: Manual review needed',
            'severity': 'INFO',
            'evidence': {'note': 'Verify breed-sensitive data is properly classified'},
            'recommendation': 'Review data classification policy for breed-specific medical conditions'
        })

        return findings


# To use this plugin:
# 1. Copy to plugins/ directory
# 2. Run: python3 scripts/plugin_manager.py --run https://target.com --level 3
# 3. Or integrate into run_assessment.py to auto-load plugins
