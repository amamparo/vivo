default:
    @just --list

poetry_cmd := "VIRTUAL_ENV=" + justfile_directory() + "/.venv PATH=" + justfile_directory() + "/.venv/bin:$PATH poetry"
_ts := "perl -pe 'use POSIX \"strftime\"; BEGIN { $| = 1 } $_ = strftime(\"%Y-%m-%d %H:%M:%S \", localtime) . $_'"

install:
    git submodule update --init
    python3.13 -m venv .venv
    {{poetry_cmd}} install
    cd ui && npm install

build:
    cd ui && npm run build

dev:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p logs
    trap 'kill 0' EXIT
    {{poetry_cmd}} run uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | {{_ts}} | tee logs/server.log &
    (cd ui && npm run dev) 2>&1 | {{_ts}} | tee logs/ui.log &
    wait

dev-server:
    mkdir -p logs
    {{poetry_cmd}} run uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | {{_ts}} | tee logs/server.log

dev-ui:
    mkdir -p logs
    cd ui && npm run dev 2>&1 | {{_ts}} | tee ../logs/ui.log

run:
    mkdir -p logs
    {{poetry_cmd}} run uvicorn server.main:app --host 0.0.0.0 --port 8000 2>&1 | {{_ts}} | tee logs/server.log

setup:
    {{poetry_cmd}} run python setup_remote_script.py

test:
    {{poetry_cmd}} run pytest
    cd ui && npm test

check:
    cd ui && npm run check
    npx pyright
