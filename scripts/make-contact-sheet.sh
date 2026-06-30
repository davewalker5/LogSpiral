#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$(dirname "$0")/.." ; pwd -P )
. "$PROJECT_ROOT/venv/bin/activate"

python "$PROJECT_ROOT/src/make_contact_sheet.py" "$@"
