#!/usr/bin/env python3
"""
Sanitize evidence by redacting PII and sensitive data.
Prevents accidental leakage of real customer data in reports.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

class Sanitizer:
    """Redact PII patterns from evidence"""

    # Pattern definitions with safe replacements
    PATTERNS = {
        'email': {
            'regex': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'replace': '[EMAIL]'
        },
        'phone': {
            'regex': r'\+?[0-9]{10,15}',
            'replace': '[PHONE]'
        },
        'dni': {
            'regex': r'\b\d{7,8}\b',
            'replace': '[DNI]'
        },
        'jwt': {
            'regex': r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            'replace': '[JWT]'
        },
        'api_key': {
            'regex': r'[a-z0-9_]{32,}',
            'replace': '[API_KEY]'
        },
        'supabase_key': {
            'regex': r'(eyJ[A-Za-z0-9_-]*\.){2}[A-Za-z0-9_-]*',
            'replace': '[SUPABASE_KEY]'
        },
        'database_url': {
            'regex': r'postgresql://[a-zA-Z0-9._:-]+@[a-zA-Z0-9.-]+:[0-9]+/\w+',
            'replace': '[DATABASE_URL]'
        },
        'ipv4': {
            'regex': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'replace': '[IPV4]'
        },
        'credit_card': {
            'regex': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'replace': '[CREDIT_CARD]'
        },
        'ssn': {
            'regex': r'\b\d{3}-\d{2}-\d{4}\b',
            'replace': '[SSN]'
        },
    }

    def __init__(self, aggressive=False):
        """
        Initialize sanitizer.

        Args:
            aggressive: If True, also redact IPv4 and other less risky patterns
        """
        self.aggressive = aggressive
        self.patterns = self.PATTERNS if aggressive else {
            k: v for k, v in self.PATTERNS.items()
            if k not in ['ipv4']  # Don't redact IPs unless aggressive
        }

    def sanitize_string(self, text: str) -> str:
        """Redact PII from a string"""
        if not isinstance(text, str):
            return text

        for pattern_name, pattern_config in self.patterns.items():
            text = re.sub(
                pattern_config['regex'],
                pattern_config['replace'],
                text,
                flags=re.IGNORECASE
            )

        return text

    def sanitize_dict(self, data: Dict) -> Dict:
        """Recursively redact PII from a dict"""
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            sanitized[key] = self.sanitize_value(value)

        return sanitized

    def sanitize_list(self, data: List) -> List:
        """Recursively redact PII from a list"""
        if not isinstance(data, list):
            return data

        return [self.sanitize_value(item) for item in data]

    def sanitize_value(self, value: Any) -> Any:
        """Sanitize any value type"""
        if isinstance(value, str):
            return self.sanitize_string(value)
        elif isinstance(value, dict):
            return self.sanitize_dict(value)
        elif isinstance(value, list):
            return self.sanitize_list(value)
        else:
            return value

    def sanitize_json_file(self, input_file: Path, output_file: Path = None) -> Path:
        """Sanitize a JSON file"""
        if output_file is None:
            output_file = input_file.with_stem(f"{input_file.stem}_sanitized")

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        sanitized = self.sanitize_value(data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sanitized, f, indent=2)

        return output_file

    def sanitize_text_file(self, input_file: Path, output_file: Path = None) -> Path:
        """Sanitize a text file"""
        if output_file is None:
            output_file = input_file.with_stem(f"{input_file.stem}_sanitized")

        with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        sanitized = self.sanitize_string(content)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sanitized)

        return output_file

    def sanitize_directory(self, directory: Path, pattern: str = "*", output_dir: Path = None) -> Path:
        """Sanitize all files matching pattern in directory"""
        if output_dir is None:
            output_dir = directory / "sanitized"

        output_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for file in directory.glob(pattern):
            if file.is_file():
                try:
                    if file.suffix == '.json':
                        self.sanitize_json_file(file, output_dir / file.name)
                    else:
                        self.sanitize_text_file(file, output_dir / file.name)
                    count += 1
                except Exception as e:
                    print(f"⚠️  Failed to sanitize {file}: {e}")

        print(f"✅ Sanitized {count} files to {output_dir}")
        return output_dir


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sanitize evidence by redacting PII.")
    parser.add_argument("input", help="Input file or directory to sanitize")
    parser.add_argument("--output", help="Output file/directory (default: _sanitized suffix)")
    parser.add_argument("--aggressive", action="store_true", help="Also redact IPs and other patterns")
    parser.add_argument("--pattern", default="*", help="File pattern to match (default: *)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    sanitizer = Sanitizer(aggressive=args.aggressive)

    if input_path.is_file():
        if input_path.suffix == '.json':
            result = sanitizer.sanitize_json_file(input_path, output_path)
        else:
            result = sanitizer.sanitize_text_file(input_path, output_path)
        print(f"✅ Sanitized: {result}")
    elif input_path.is_dir():
        sanitizer.sanitize_directory(input_path, pattern=args.pattern, output_dir=output_path)
    else:
        print(f"❌ Path not found: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
