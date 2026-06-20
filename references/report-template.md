# Report Template

Use this structure for final reports.

## Executive Summary

- Scope
- Date
- Depth level
- Overall risk
- Most important confirmed issue

## Scope

- URLs
- Accounts/roles tested
- Environments
- Explicit exclusions

## Tools Used

Table columns:

- Tool
- Purpose
- Intensity
- Result
- Evidence file

## Findings

For each finding:

- Title
- Severity: Critical, High, Medium, Low, Informational
- Status: Confirmed, Likely, Needs source review, False positive
- Impact in plain language
- Evidence
- Affected targets
- Fix
- Retest steps

## Enterprise Tracking

For Level 5 reports, add:

- Owner
- Due date
- Remediation status: open, in progress, fixed, accepted risk
- Retest date
- Retest result
- Regression test added: yes/no

## Normal / Expected Results

List controls that worked.

## Review Items

List issues that are not confirmed exploitable but deserve engineering review.

## Fix Now

List confirmed vulnerabilities in priority order.

## Evidence Index

List local files. Do not include raw secrets, tokens, passwords, or private values.

## Sanitization Notes

State what was intentionally redacted or deleted.
