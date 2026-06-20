#!/usr/bin/env python3
import argparse
import html
import re
import shutil
import subprocess
from pathlib import Path

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: Arial, sans-serif; color: #1f2933; line-height: 1.45; font-size: 11.5pt; }
h1 { font-size: 24pt; margin: 0 0 10px; color: #0f172a; }
h2 { font-size: 15pt; border-bottom: 1px solid #d0d7de; padding-bottom: 4px; margin-top: 22px; }
h3 { font-size: 12.5pt; margin-top: 16px; }
code { font-family: Consolas, monospace; font-size: 10pt; background: #f3f4f6; padding: 1px 3px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; padding: 10px; white-space: pre-wrap; font-size: 9.5pt; }
li { margin: 3px 0; }
.meta { color: #4b5563; }
"""

SECRET_PATTERNS = [
    (re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"), "[REDACTED_JWT]"),
    (re.compile(r"(?i)(password|contrase[a-zñ]+|passwd|token|apikey|api_key|secret)(\\s*[:=]\\s*)([^\\s`'\"]+)"), r"\1\2[REDACTED]"),
]

def sanitize(text):
    clean = text
    for pattern, replacement in SECRET_PATTERNS:
        clean = pattern.sub(replacement, clean)
    return clean

def inline_format(text):
    escaped = html.escape(text)
    return re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", escaped)

def markdown_to_html(markdown):
    lines = markdown.splitlines()
    out = []
    in_list = False
    in_code = False
    code_lines = []

    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("<pre>" + html.escape("\n".join(code_lines)) + "</pre>")
                code_lines = []
                in_code = False
            else:
                if in_list:
                    out.append("</ul>")
                    in_list = False
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h1>{inline_format(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{inline_format(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{inline_format(line[4:].strip())}</h3>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline_format(line[2:].strip())}</li>")
        elif not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{inline_format(line.strip())}</p>")

    if in_code:
        out.append("<pre>" + html.escape("\n".join(code_lines)) + "</pre>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)

def render_pdf(html_path, pdf_path):
    chromium = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    if chromium:
        cmd = [chromium, "--headless", "--no-sandbox", "--disable-gpu", "--disable-crash-reporter", f"--print-to-pdf={pdf_path}", html_path.as_uri()]
        return subprocess.run(cmd, check=False).returncode
    weasyprint = shutil.which("weasyprint")
    if weasyprint:
        return subprocess.run([weasyprint, str(html_path), str(pdf_path)], check=False).returncode
    return 127

def main():
    parser = argparse.ArgumentParser(description="Generate sanitized HTML/PDF report from an assessment summary markdown.")
    parser.add_argument("summary", help="Path to resumen.md or another markdown summary")
    parser.add_argument("--title", default="Security Assessment Report")
    parser.add_argument("--html", default=None)
    parser.add_argument("--pdf", default=None)
    args = parser.parse_args()

    summary_path = Path(args.summary).resolve()
    base = summary_path.parent
    html_path = Path(args.html).resolve() if args.html else base / "informe.html"
    pdf_path = Path(args.pdf).resolve() if args.pdf else base / "informe.pdf"

    markdown = sanitize(summary_path.read_text(encoding="utf-8", errors="replace"))
    body = markdown_to_html(markdown)
    document = f"<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\"><title>{html.escape(args.title)}</title><style>{CSS}</style></head><body>{body}</body></html>"
    html_path.write_text(document, encoding="utf-8")

    pdf_result = render_pdf(html_path, pdf_path)
    print(f"HTML: {html_path}")
    if pdf_result == 0 and pdf_path.exists():
        print(f"PDF: {pdf_path}")
    else:
        print("PDF: not generated; install/fix chromium or weasyprint")

if __name__ == "__main__":
    main()
