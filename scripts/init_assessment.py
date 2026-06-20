#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path

STAGES = ["recon", "content", "app", "auth", "data", "vuln", "report"]

def slugify(value):
    allowed = []
    for ch in value.lower():
        if ch.isalnum():
            allowed.append(ch)
        elif ch in ["-", "_", ".", " "]:
            allowed.append("-")
    slug = "".join(allowed).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "assessment"

def main():
    parser = argparse.ArgumentParser(description="Create a security assessment report workspace.")
    parser.add_argument("name", help="Assessment name, e.g. neovet or huellas")
    parser.add_argument("--out", default="reportes", help="Base output directory")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2)
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path(args.out) / f"{slugify(args.name)}_{stamp}"
    root.mkdir(parents=True, exist_ok=True)
    for stage in STAGES:
        (root / stage).mkdir(exist_ok=True)

    summary = root / "resumen.md"
    summary.write_text(
        f"# Security assessment - {args.name}\n\n"
        f"- Created: {stamp}\n"
        f"- Depth level: {args.level}\n\n"
        "## Scope\n\n"
        "## Tools Used\n\n"
        "## Normal / Expected\n\n"
        "## Needs Review\n\n"
        "## Fix Now\n\n"
        "## Evidence Index\n",
        "\n## Enterprise Tracking\n",
        encoding="utf-8",
    )

    print(root)

if __name__ == "__main__":
    main()
