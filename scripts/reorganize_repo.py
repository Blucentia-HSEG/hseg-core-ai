#!/usr/bin/env python3
"""
Reorganize repository content:
 - Create docs/ and keep relevant documentation there
 - Move all other markdown docs to dump/document/
 - Move redundant/non-essential folders to dump/

Relevant docs kept in docs/:
 - README.md (root)
 - DOCKER_DEPLOYMENT.md
 - PRODUCTION_GUIDE.md
 - frontend/README.md (renamed to frontend.md)
 - scripts/README.md (renamed to scripts.md)

Everything else *.md is moved to dump/document/.
Also moves tests/ folder to dump/ if present.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / 'dump'
DOCS = ROOT / 'docs'
DOC_DUMP = DUMP / 'document'


def safe_move(src: Path, dest: Path):
    if not src.exists():
        return 'missing'
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(src), str(dest))
        return 'moved'
    except Exception as e:
        return f'error: {e}'


def main():
    DUMP.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    DOC_DUMP.mkdir(parents=True, exist_ok=True)

    report = {'moved_docs': [], 'moved_dump_docs': [], 'moved_misc': [], 'skipped': []}

    # Relevant docs to keep
    keep_map = {
        ROOT / 'README.md': DOCS / 'README.md',
        ROOT / 'DOCKER_DEPLOYMENT.md': DOCS / 'DOCKER_DEPLOYMENT.md',
        ROOT / 'PRODUCTION_GUIDE.md': DOCS / 'PRODUCTION_GUIDE.md',
        ROOT / 'frontend' / 'README.md': DOCS / 'frontend.md',
        ROOT / 'scripts' / 'README.md': DOCS / 'scripts.md',
    }

    for src, dest in keep_map.items():
        res = safe_move(src, dest)
        if res == 'moved':
            report['moved_docs'].append(str(dest.relative_to(ROOT)))
        elif res != 'missing':
            report['skipped'].append((str(src.relative_to(ROOT)), res))

    # Move all other markdown to dump/document (excluding docs/ itself)
    for path in ROOT.rglob('*.md'):
        if path.is_dir():
            continue
        # Skip docs folder and files already moved into docs
        if DOCS in path.parents:
            continue
        # Skip kept docs already moved
        if any(path.samefile(k) for k in keep_map.keys() if k.exists()):
            continue
        # Place into dump/document preserving only filename to avoid deep trees
        dest = DOC_DUMP / path.name
        res = safe_move(path, dest)
        if res == 'moved':
            report['moved_dump_docs'].append(str(dest.relative_to(ROOT)))
        elif res != 'missing':
            report['skipped'].append((str(path.relative_to(ROOT)), res))

    # Move tests/ folder to dump/
    tests_dir = ROOT / 'tests'
    if tests_dir.exists():
        dest = DUMP / 'tests'
        try:
            shutil.move(str(tests_dir), str(dest))
            report['moved_misc'].append('tests/')
        except Exception as e:
            report['skipped'].append(('tests/', f'error: {e}'))

    # Print a concise report
    print('Moved into docs/:')
    for p in report['moved_docs']:
        print('  -', p)
    print('Moved into dump/document/:')
    for p in report['moved_dump_docs']:
        print('  -', p)
    print('Moved miscellaneous:')
    for p in report['moved_misc']:
        print('  -', p)
    if report['skipped']:
        print('Skipped:')
        for item, reason in report['skipped']:
            print(f'  - {item} ({reason})')


if __name__ == '__main__':
    main()

