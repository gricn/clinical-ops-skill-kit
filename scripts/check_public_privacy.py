"""Check staged public files for risky paths and common sensitive patterns.

Use before commits. Input: Git index. Output: locations only, never matched values.
Run: .venv/bin/python scripts/check_public_privacy.py
This heuristic does not verify business anonymity or clean existing Git history.
"""
import re
import subprocess
from pathlib import PurePosixPath

PATTERNS = {
    'local home path': re.compile(rb'/(?:Users|home)/[A-Za-z0-9_.-]+/'),
    'private key': re.compile(rb'-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----'),
    'access token': re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{30,})'),
    'personal email': re.compile(rb'[\w.+-]+@(?:gmail|outlook|qq|hotmail)\.com', re.I),
}

def forbidden_path(name):
    p = PurePosixPath(name)
    if p.parts[0] in {'workspaces', 'secrets', 'surgery_records'}:
        return p.name not in {'README.md', '.gitkeep'}
    return p.name.startswith('.env') or p.suffix in {'.pem', '.key'} or any(x.startswith('browser-profile') for x in p.parts)

def violations(name, content):
    result = ['runtime or credential path'] if forbidden_path(name) else []
    result += [label for label, pattern in PATTERNS.items() if pattern.search(content)]
    return result

def main():
    names = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z']).decode().split('\0')
    failures = []
    for name in filter(None, names):
        content = subprocess.check_output(['git', 'show', ':' + name])
        failures += [(name, label) for label in violations(name, content)]
    for name, label in failures:
        print(f'{name}: {label}')
    print('Public privacy gate: ' + ('FAILED' if failures else 'passed (manual semantic review still required)'))
    return bool(failures)

if __name__ == '__main__':
    raise SystemExit(main())
