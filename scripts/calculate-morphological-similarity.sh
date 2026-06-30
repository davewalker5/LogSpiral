#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$(dirname "$0")/.." ; pwd -P )
. "$PROJECT_ROOT/venv/bin/activate"

python "$PROJECT_ROOT/src/calculate-morphological-similarity.py" \
    --markdown "$PROJECT_ROOT/data/outputs/similarity.md" \
    --matrix-csv "$PROJECT_ROOT/data/outputs/similarity-matrix.csv" \
    --pairwise-csv "$PROJECT_ROOT/data/outputs/pairwise-comparison.csv" \
    --nearest-csv "$PROJECT_ROOT/data/outputs/nearest-neighbour.csv" \
    --matrix-plot "$PROJECT_ROOT/data/outputs/similarity-matrix.png" \
    --dendrogram-plot "$PROJECT_ROOT/data/outputs/similarity-dendrogram.png" \
    --json "$PROJECT_ROOT/data/outputs/similarity.json"
