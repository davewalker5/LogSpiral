#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$(dirname "$0")/.." ; pwd -P )
. "$PROJECT_ROOT/venv/bin/activate"

declare -a GROUPINGS=(
    "shell"
    "family"
    "geometry"
    "view"
    "render"
)


for grouping in "${GROUPINGS[@]}"; do
    python "$PROJECT_ROOT/src/make-contact-sheet.py" --group-by $grouping
done
