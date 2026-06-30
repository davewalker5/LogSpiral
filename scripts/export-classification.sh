#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$(dirname "$0")/.." ; pwd -P )
. "$PROJECT_ROOT/venv/bin/activate"

python "$PROJECT_ROOT/src/export_preset_classification.py" \
    --output "$PROJECT_ROOT/data/outputs/shell-classification.csv"
