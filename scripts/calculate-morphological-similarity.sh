#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$(dirname "$0")/.." ; pwd -P )
. "$PROJECT_ROOT/venv/bin/activate"

python "$PROJECT_ROOT/src/calculate_morphological_similarity.py" \
    --markdown "$PROJECT_ROOT/data/similarity/similarity.md" \
    --matrix-csv "$PROJECT_ROOT/data/similarity/similarity-matrix.csv" \
    --pairwise-csv "$PROJECT_ROOT/data/similarity/pairwise-comparison.csv" \
    --nearest-csv "$PROJECT_ROOT/data/similarity/nearest-neighbour.csv" \
    --matrix-plot "$PROJECT_ROOT/data/similarity/similarity-matrix.png" \
    --dendrogram-plot "$PROJECT_ROOT/data/similarity/similarity-dendrogram.png" \
    --json "$PROJECT_ROOT/data/similarity/similarity.json"
