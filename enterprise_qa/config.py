"""Minimal local .env loading; process environment takes precedence."""
import os
from pathlib import Path

def load_env(path='.env'):
    source = Path(path)
    if not source.exists(): return
    for number, raw in enumerate(source.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'): continue
        if line.startswith('export '): line = line[7:].strip()
        key, separator, value = line.partition('=')
        if not separator or not key.strip().isidentifier():
            raise ValueError(f'Invalid environment assignment at line {number}')
        value = value.strip()
        if value[:1] in ('"', "'"):
            if len(value)<2 or value[-1]!=value[0]: raise ValueError(f'Invalid quote at line {number}')
            value=value[1:-1]
        else:
            value=value.split(' #',1)[0].rstrip()
        os.environ.setdefault(key.strip(),value)
