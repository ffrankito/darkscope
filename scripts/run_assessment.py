#!/usr/bin/env python3
import argparse
import os
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from check_tools import find_tool

STAGES_BY_LEVEL = {
    0: ["recon"],
    1: ["recon", "content"],
    2: ["recon", "content", "app", "vuln"],
    3: ["recon", "content", "app", "data", "vuln"],
    4: ["recon", "content", "app", "data", "vuln"],
}

PROD_MARKERS = ["vercel.app", "prod", "production"]

def is_prod(target, env):
    if env == "production":
        return True
    if env in ["staging", "local", "lab"]:
        return False
    lower = target.lower()
    return any(marker in lower for marker in PROD_MARKERS)

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
    return slug or "target"

def host_from_target(target):
    parsed = urlparse(target)
    if parsed.hostname:
        return parsed.hostname
    return target.split("/")[0].split(":")[0]

def quote_cmd(command):
    return " ".join(shlex.quote(part) for part in command)

def run_command(command, output_file, execute, timeout):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    rendered = quote_cmd(command)
    if not execute:
        output_file.write_text(rendered + "\n", encoding="utf-8")
        return 0

    with output_file.open("w", encoding="utf-8", errors="replace") as handle:
        handle.write("$ " + rendered + "\n\n")
        handle.flush()
        try:
            proc = subprocess.run(
                command,
                stdout=handle,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
            )
            return proc.returncode
        except subprocess.TimeoutExpired:
            handle.write(f"\n[TIMEOUT] stopped after {timeout} seconds\n")
            return 124

def tool(name):
    return find_tool(name)

def build_commands(target, level, env, outdir):
    host = host_from_target(target)
    prod = is_prod(target, env)
    commands = []

    def add(stage, name, cmd, seconds=300):
        commands.append((stage, name, cmd, seconds))

    if tool("curl"):
        add("recon", "headers", [tool("curl"), "-sk", "-D", "-", "-o", "/dev/null", target], 60)
    if tool("whatweb"):
        add("recon", "whatweb", [tool("whatweb"), "-a", "3", target], 120)
    if level >= 1 and tool("wafw00f"):
        add("recon", "wafw00f", [tool("wafw00f"), target], 180)
    if level >= 1 and tool("nmap"):
        add("recon", "nmap_web_ports", [tool("nmap"), "-sV", "-sC", "-Pn", "-p", "80,443", host], 600)
    if level >= 1 and target.startswith("https://") and tool("sslscan"):
        add("recon", "sslscan", [tool("sslscan"), host], 300)

    if level >= 1 and tool("katana"):
        add("content", "katana", [tool("katana"), "-u", target, "-d", "2", "-silent"], 600)
    if level >= 2 and tool("feroxbuster"):
        add("content", "feroxbuster_low_rate", [tool("feroxbuster"), "-u", target, "-k", "-x", "js,json,txt", "-t", "5", "--rate-limit", "5", "-w", "/usr/share/wordlists/dirb/common.txt"], 900)
    if level >= 2 and tool("ffuf"):
        add("content", "ffuf_common_low_rate", [tool("ffuf"), "-u", target.rstrip("/") + "/FUZZ", "-w", "/usr/share/wordlists/dirb/common.txt", "-rate", "5", "-mc", "200,204,301,302,307,401,403"], 900)

    if tool("curl"):
        for route in ["/", "/login", "/dashboard", "/api/me", "/api/health", "/robots.txt", "/sitemap.xml"]:
            add("app", "route_" + slugify(route), [tool("curl"), "-sk", "-o", "/dev/null", "-w", "%{http_code} %{url_effective}\\n", target.rstrip("/") + route], 60)
        add("app", "cors_options", [tool("curl"), "-sk", "-D", "-", "-o", "/dev/null", "-X", "OPTIONS", "-H", "Origin: https://security-review.invalid", target], 60)

    if level >= 2 and tool("nikto"):
        add("vuln", "nikto", [tool("nikto"), "-h", target], 1200)
    if level >= 2 and tool("nuclei"):
        nuclei_cmd = [tool("nuclei"), "-u", target, "-severity", "medium,high,critical", "-silent"]
        add("vuln", "nuclei_priority", nuclei_cmd, 1200)
    if level >= 2 and tool("zap.sh"):
        add("vuln", "zap_zapit", [tool("zap.sh"), "-cmd", "-zapit", target], 1200)
    if level >= 3 and tool("sqlmap"):
        add("vuln", "sqlmap_low_risk_placeholder", [tool("sqlmap"), "-u", target, "--batch", "--level", "1", "--risk", "1", "--smart"], 1200)

    if prod and level >= 3:
        commands = [item for item in commands if item[1] != "sqlmap_low_risk_placeholder"]

    return commands

def main():
    parser = argparse.ArgumentParser(description="Run or plan a staged authorized security assessment.")
    parser.add_argument("target", help="Base URL to assess")
    parser.add_argument("--name", default=None, help="Assessment name")
    parser.add_argument("--out", default="reportes", help="Base output directory")
    parser.add_argument("--level", type=int, choices=range(0, 5), default=2)
    parser.add_argument("--env", choices=["auto", "production", "staging", "local", "lab"], default="auto")
    parser.add_argument("--stage", choices=["all", "recon", "content", "app", "data", "vuln"], default="all")
    parser.add_argument("--execute", action="store_true", help="Run commands. Without this flag, only writes the plan.")
    parser.add_argument("--allow-level-4", action="store_true", help="Allow level 4 when env is lab/staging/local.")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()

    prod = is_prod(args.target, args.env)
    if prod and args.level >= 4:
        raise SystemExit("Refusing level 4 against production. Use staging/local/lab with fake data.")
    if args.level == 4 and not args.allow_level_4:
        raise SystemExit("Level 4 requires --allow-level-4 and a non-production environment.")

    name = args.name or host_from_target(args.target)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path(args.out) / f"{slugify(name)}_{stamp}"
    root.mkdir(parents=True, exist_ok=True)
    for stage in ["recon", "content", "app", "data", "vuln", "report"]:
        (root / stage).mkdir(exist_ok=True)

    stages = STAGES_BY_LEVEL[args.level] if args.stage == "all" else [args.stage]
    commands = [c for c in build_commands(args.target, args.level, args.env, root) if c[0] in stages]

    plan_file = root / "run_plan.txt"
    with plan_file.open("w", encoding="utf-8") as handle:
        handle.write(f"target={args.target}\nlevel={args.level}\nenv={args.env}\nproduction_detected={prod}\nexecute={args.execute}\n\n")
        for stage, name, cmd, seconds in commands:
            handle.write(f"[{stage}] {name}: {quote_cmd(cmd)} (timeout={min(seconds, args.timeout)}s)\n")

    for stage, name, cmd, seconds in commands:
        safe_name = slugify(name)
        output = root / stage / f"{safe_name}.txt"
        run_command(cmd, output, args.execute, min(seconds, args.timeout))

    summary = root / "resumen.md"
    summary.write_text(
        f"# Security assessment\n\n- Target: {args.target}\n- Level: {args.level}\n- Environment: {args.env}\n- Production detected: {prod}\n- Executed: {args.execute}\n\n"
        f"## Plan\n\nSee `{plan_file.name}`.\n\n## Findings\n\n- Review command outputs and classify as normal, needs review, or fix now.\n",
        encoding="utf-8",
    )
    print(root)

if __name__ == "__main__":
    main()

