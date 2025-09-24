#!/usr/bin/env python3
"""
Organize repository by moving non-essential files into ./dump

Non-essential = not directly required for running the API, frontend, or dockerization.
You can adjust the FILES_TO_MOVE list below before running.

Usage:
  python scripts/organize_to_dump.py

This will create the dump/ folder (if missing) and move listed files there.
It is idempotent and will skip files that are already moved or missing.
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / 'dump'

# Curated list based on current repo structure. Adjust as needed.
FILES_TO_MOVE = [
    'hseg_comprehensive_analysis.ipynb',
    'improved_hseg_survey.md',
    'ENTERPRISE_READY_SUMMARY.md',
    'TESTING_GUIDE.md',
    'hseg_enterprise_dashboard.py',
    'merge_hseg_data.py',
    'clean_hseg_dataset.py',
    'generate_demographics_final.py',
    'complete_test.py',
    'simple_test.py',
    'test_api.py',
    'test_enterprise_functionality.py',
    'test_complete_functionality.py',
    'test_pipeline.py',
    'HSEG_Comprehensive_Scoring_Documentation.md'
]

# Optional patterns to move many files at once without touching core app/frontend/docker
PATTERNS = [
    '*.ipynb',
    '*.png', '*.jpg', '*.jpeg', '*.svg',
    'README_*.md',
]

def main():
    DUMP.mkdir(exist_ok=True)
    moved = []
    skipped = []
    for rel in FILES_TO_MOVE:
        src = ROOT / rel
        if not src.exists():
            skipped.append((rel, 'missing'))
            continue
        dest = DUMP / src.name
        try:
            shutil.move(str(src), str(dest))
            moved.append(rel)
        except Exception as e:
            skipped.append((rel, f'error: {e}'))

    # Pattern-based moves (safe guard: skip known core directories)
    core_dirs = {'app', 'frontend', 'docker', 'scripts', '.git', 'dump'}
    for pattern in PATTERNS:
        for path in ROOT.glob(pattern):
            if not path.exists() or path.is_dir():
                continue
            if any(str(path).startswith(str(ROOT / d)) for d in core_dirs):
                continue
            dest = DUMP / path.name
            try:
                shutil.move(str(path), str(dest))
                moved.append(str(path.relative_to(ROOT)))
            except Exception as e:
                skipped.append((str(path), f'error: {e}'))

    print('Moved to dump/:')
    for m in moved:
        print(f'  - {m}')
    if skipped:
        print('Skipped:')
        for rel, reason in skipped:
            print(f'  - {rel} ({reason})')

if __name__ == '__main__':
    main()
