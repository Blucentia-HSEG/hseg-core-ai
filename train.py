#!/usr/bin/env python3
"""
Train HSEG models with versioned artifact output.

Usage examples:
  python train.py --version v1.1.0 --all
  python train.py --version 2025-09-24 --individual --text

Artifacts will be saved under:
  app/models/trained/                (latest)
  app/models/trained/{version}/      (versioned copy)
"""

import argparse
import json
import shutil
from pathlib import Path

from scripts.train_all_from_final_dataset import (
    load_data,
    train_individual,
    train_text,
    train_organizational,
)

OUT_DIR = Path('app/models/trained')


def main():
    parser = argparse.ArgumentParser(description='Train HSEG models with versioned artifacts')
    parser.add_argument('--version', required=True, help='Version tag for artifacts, e.g., v1.1.0 or 2025-09-24')
    parser.add_argument('--individual', action='store_true', help='Train individual model')
    parser.add_argument('--text', action='store_true', help='Train text model')
    parser.add_argument('--org', action='store_true', help='Train organizational models')
    parser.add_argument('--all', action='store_true', help='Train all models')
    args = parser.parse_args()

    if not (args.individual or args.text or args.org or args.all):
        parser.error('Select at least one: --individual, --text, --org, or --all')

    df = load_data('data/hseg_final_dataset.csv')
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report = {}

    if args.individual or args.all:
        print('Training IndividualRiskPredictor...')
        report['individual'] = train_individual(df)

    if args.text or args.all:
        print('Training TextRiskClassifier...')
        report['text'] = {'accuracy': train_text(df)}

    if args.org or args.all:
        print('Training Organizational models...')
        org_acc_rmse = train_organizational(df)
        report['organizational'] = {'accuracy': org_acc_rmse[0], 'turnover_rmse': org_acc_rmse[1]} if org_acc_rmse else {}

    # Write aggregated report
    (OUT_DIR / 'training_report.json').write_text(json.dumps(report, indent=2))

    # Copy artifacts to versioned folder
    version_dir = OUT_DIR / args.version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ['individual_risk_model.pkl', 'text_risk_classifier.pkl', 'organizational_risk_model.pkl', 'training_report.json']:
        src = OUT_DIR / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    print(f'Artifacts copied to {version_dir}')


if __name__ == '__main__':
    main()

