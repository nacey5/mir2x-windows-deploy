"""Read-only compatibility check; never start/stop a server or write its files."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'overlays' / 'playability'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(server_root):
    manifest = json.loads((OVERLAY / 'baseline.json').read_text(encoding='utf-8'))
    script_root = Path(server_root) / 'script'
    problems = []
    for relative, expected in manifest['dependencies'].items():
        path = script_root / relative
        if not path.is_file():
            problems.append('Missing dependency: ' + relative)
        elif digest(path) != expected:
            problems.append('Changed dependency; review required: ' + relative)
    for patch in (OVERLAY / 'server' / 'script').rglob('*.lua'):
        relative = patch.relative_to(OVERLAY / 'server' / 'script').as_posix()
        target = script_root / relative
        if relative in manifest['replace_empty']:
            if not target.is_file():
                problems.append('Expected placeholder missing: ' + relative)
            elif target.stat().st_size != 0 and digest(target) != digest(patch):
                problems.append('Refusing to overwrite customized NPC: ' + relative)
        elif target.exists() and (not target.is_file() or digest(target) != digest(patch)):
            problems.append('New script name already used: ' + relative)
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-root', type=Path, required=True)
    args = parser.parse_args()
    problems = check(args.server_root)
    print(json.dumps({'compatible': not problems, 'problems': problems,
                      'scope': 'script compatibility only; no runtime/playtest certification'},
                     ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
