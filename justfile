default:
    @just --list

poetry_cmd := "VIRTUAL_ENV=" + justfile_directory() + "/.venv PATH=" + justfile_directory() + "/.venv/bin:$PATH poetry"

install:
    python3.13 -m venv .venv
    {{poetry_cmd}} install
    cd ui && npm install

build:
    cd ui && npm run build

dev-ui:
    cd ui && npm run dev

run:
    {{poetry_cmd}} run uvicorn server.main:app --host 0.0.0.0 --port 8000

dev:
    {{poetry_cmd}} run uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

setup:
    {{poetry_cmd}} run python setup_abletonosc.py

test:
    {{poetry_cmd}} run pytest
    cd ui && npm test

check:
    cd ui && npm run check
