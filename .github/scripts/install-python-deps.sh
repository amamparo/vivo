#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
.venv/bin/pip install poetry
VIRTUAL_ENV=$(pwd)/.venv PATH=$(pwd)/.venv/bin:$PATH poetry install
