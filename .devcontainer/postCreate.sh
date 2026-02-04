#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install poetry

poetry config virtualenvs.in-project true
poetry install --with dev --no-interaction --no-ansi
