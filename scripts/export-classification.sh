#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$(dirname "$0")/.." ; pwd -P )
. "$PROJECT_ROOT/venv/bin/activate"

python "$PROJECT_ROOT/src/export_preset_classification.py" \
    --json "$PROJECT_ROOT/data/similarity/shell-classification.json" \
    --csv "$PROJECT_ROOT/data/similarity/shell-classification.csv"
