#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import shutil

LEVEL_TOOLS = {
    0: ["curl", "whatweb"],
    1: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan"],
    2: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap.sh"],
    3: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap.sh", "sqlmap"],
    4: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap.sh", "sqlmap"],
}

APT_HINTS = {
    "zap.sh": "zaproxy",
    "katana": "golang-go; then go install github.com/projectdiscovery/katana/cmd/katana@latest",
    "gitleaks": "gitleaks",
    "trufflehog": "trufflehog",
}

FALLBACK_PATHS = {
    "katana": ["~/go/bin/katana"],
    "zap.sh": ["/usr/share/zaproxy/zap.sh"],
}

def find_tool(tool):
    path = shutil.which(tool)
    if path:
        return path
    for candidate in FALLBACK_PATHS.get(tool, []):
        expanded = Path(os.path.expanduser(candidate))
        if expanded.exists() and os.access(expanded, os.X_OK):
            return str(expanded)
    return None

def main():
    parser = argparse.ArgumentParser(description="Check installed tools for a security review depth level.")
    parser.add_argument("--level", type=int, choices=range(0, 5), default=2)
    args = parser.parse_args()

    tools = LEVEL_TOOLS[args.level]
    missing = []

    print(f"# Tool check for level {args.level}\n")
    for tool in tools:
        path = find_tool(tool)
        if path:
            print(f"OK      {tool:14} {path}")
        else:
            missing.append(tool)
            print(f"MISSING {tool:14}")

    if missing:
        apt_names = [APT_HINTS.get(tool, tool) for tool in missing]
        print("\n# Install hint")
        for hint in sorted(set(apt_names)):
            if hint.startswith("golang-go;"):
                print("sudo apt install -y golang-go")
                print(hint.split("; then ", 1)[1])
            else:
                print("sudo apt install -y " + hint)
    else:
        print("\nAll expected tools for this level were found.")

if __name__ == "__main__":
    main()
