#!/usr/bin/env python3
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
import shutil

LEVEL_TOOLS = {
    0: ["curl", "whatweb"],
    1: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan"],
    2: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap"],
    3: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap", "sqlmap"],
    4: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap", "sqlmap"],
    5: ["curl", "jq", "nmap", "whatweb", "wafw00f", "sslscan", "nikto", "nuclei", "katana", "gitleaks", "trufflehog", "feroxbuster", "ffuf", "zap", "sqlmap", "semgrep", "trivy"],
}

TOOLS_INFO = {
    "curl": {"critical": True, "apt": "curl", "brew": "curl", "choco": "curl"},
    "jq": {"critical": True, "apt": "jq", "brew": "jq", "choco": "jq"},
    "nmap": {"critical": True, "apt": "nmap", "brew": "nmap", "choco": "nmap"},
    "whatweb": {"critical": False, "apt": "whatweb", "brew": "whatweb", "choco": "whatweb"},
    "wafw00f": {"critical": False, "apt": "python3-pip; then pip3 install wafw00f", "brew": "pip3 install wafw00f", "choco": "pip3 install wafw00f"},
    "sslscan": {"critical": False, "apt": "sslscan", "brew": "sslscan", "choco": "sslscan"},
    "nikto": {"critical": False, "apt": "nikto", "brew": "nikto", "choco": "nikto"},
    "nuclei": {"critical": False, "apt": "nuclei", "brew": "nuclei", "choco": "nuclei"},
    "katana": {"critical": False, "apt": "golang-go; then go install github.com/projectdiscovery/katana/cmd/katana@latest", "brew": "go; then go install github.com/projectdiscovery/katana/cmd/katana@latest", "choco": "golang; then go install github.com/projectdiscovery/katana/cmd/katana@latest", "fallback": "~/go/bin/katana"},
    "gitleaks": {"critical": False, "apt": "gitleaks", "brew": "gitleaks", "choco": "gitleaks"},
    "trufflehog": {"critical": False, "apt": "trufflehog", "brew": "trufflehog", "choco": "trufflehog"},
    "feroxbuster": {"critical": False, "apt": "feroxbuster", "brew": "feroxbuster", "choco": "feroxbuster"},
    "ffuf": {"critical": False, "apt": "ffuf", "brew": "ffuf", "choco": "ffuf"},
    "zap": {"critical": False, "apt": "zaproxy", "brew": "zaproxy", "choco": "owasp-zap", "docker": "owasp/zap2docker-stable", "fallback": "/usr/share/zaproxy/zap.sh"},
    "sqlmap": {"critical": False, "apt": "sqlmap", "brew": "sqlmap", "choco": "sqlmap"},
    "semgrep": {"critical": False, "apt": "semgrep", "brew": "semgrep", "choco": "semgrep"},
    "trivy": {"critical": False, "apt": "trivy", "brew": "trivy", "choco": "trivy"},
}

FALLBACK_PATHS = {
    "katana": ["~/go/bin/katana"],
    "zap": ["/usr/share/zaproxy/zap.sh", "C:\\Program Files\\OWASP\\ZAP\\zap.exe"],
}

def get_os():
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    elif system == "Windows":
        return "windows"
    return "unknown"

def find_tool(tool):
    """Find tool in PATH or fallback locations"""
    # Try different aliases
    aliases = {
        "zap": ["zap.sh", "zap", "zaproxy"],
    }

    for alias in aliases.get(tool, [tool]):
        path = shutil.which(alias)
        if path:
            return path

    # Try fallback paths
    for candidate in FALLBACK_PATHS.get(tool, []):
        expanded = Path(os.path.expanduser(candidate))
        if expanded.exists() and os.access(expanded, os.X_OK):
            return str(expanded)

    return None

def install_tool(tool, auto=False):
    """Attempt to install a tool"""
    os_type = get_os()
    info = TOOLS_INFO.get(tool, {})

    if os_type == "linux":
        cmd_key = "apt"
    elif os_type == "macos":
        cmd_key = "brew"
    elif os_type == "windows":
        cmd_key = "choco"
    else:
        print(f"❌ Unsupported OS: {os_type}")
        return False

    install_cmd = info.get(cmd_key)
    if not install_cmd:
        print(f"❌ No installation method for {tool} on {os_type}")
        return False

    if not auto:
        print(f"ℹ️  Run: {install_cmd}")
        return False

    print(f"🔧 Installing {tool}...")
    try:
        if ";" in install_cmd:
            parts = install_cmd.split("; then ")
            for part in parts:
                subprocess.run(part.split(), check=True, capture_output=True)
        else:
            if os_type == "linux":
                subprocess.run(["sudo", "apt", "install", "-y"] + install_cmd.split(), check=True)
            elif os_type == "macos":
                subprocess.run(["brew", "install"] + install_cmd.split(), check=True)
            elif os_type == "windows":
                subprocess.run(["choco", "install", "-y"] + install_cmd.split(), check=True)

        print(f"✅ {tool} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {tool}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Check/install tools for DarkScope.")
    parser.add_argument("--level", type=int, choices=range(0, 6), default=2, help="Assessment level (0-5)")
    parser.add_argument("--auto-install", action="store_true", help="Auto-install missing tools")
    parser.add_argument("--docker", action="store_true", help="Use Docker for heavy tools (ZAP)")
    args = parser.parse_args()

    tools = LEVEL_TOOLS[args.level]
    missing = []
    installed_count = 0

    print(f"🔍 Tool check for level {args.level}\n")

    for tool in tools:
        path = find_tool(tool)
        if path:
            print(f"✅ {tool:14} {path}")
        else:
            missing.append(tool)
            print(f"❌ {tool:14} MISSING")

            if args.auto_install:
                if install_tool(tool, auto=True):
                    installed_count += 1

    if missing and not args.auto_install:
        print(f"\n❌ {len(missing)} tools missing. Run with --auto-install to install them automatically.")
        print(f"\n📖 Manual installation:")
        for tool in missing:
            info = TOOLS_INFO.get(tool, {})
            os_type = get_os()
            if os_type == "linux":
                cmd = info.get("apt")
            elif os_type == "macos":
                cmd = info.get("brew")
            else:
                cmd = info.get("choco")

            if cmd:
                print(f"  {tool}: {cmd}")

    if missing:
        sys.exit(1)
    else:
        print(f"\n✅ All tools for level {args.level} are installed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
