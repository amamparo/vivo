# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
just install        # Init submodules, create .venv, poetry install, npm install
just build          # Build Svelte UI to ui/dist
just run            # Serve on :8000 (requires built UI)
just dev            # Server + UI with file-watching
just dev-server     # FastAPI with auto-reload only
just dev-ui         # Vite dev server with HMR only
just test           # Run pytest + vitest suites
just check          # Run svelte-check + pyright on remote_script
just setup          # Install LiveEarsOSC Remote Script into Ableton
```

Run a single Python test: `just test -- tests/test_solo_manager.py::TestSoloManager::test_soloing_a_track_mutes_all_others`
Run UI tests only: `cd ui && npm test`
Run a single UI test: `cd ui && npx vitest run -t "test name"`

Use `just` commands rather than bare `poetry run` — the justfile has a pyenv workaround that sets `VIRTUAL_ENV` and `PATH` explicitly.

All runtime logs go to `logs/` (gitignored):
- `logs/server.log` — FastAPI/uvicorn output
- `logs/ui.log` — Vite dev server output
- `logs/liveearsosc.log` — Ableton remote script output (written by the LiveEarsOSC ControlSurface running inside Ableton)

When diagnosing issues, check `logs/liveearsosc.log` for remote script errors — these surface Ableton-side failures that the server can't see.

## Architecture

**Communication chain:** Svelte UI ↔ WebSocket ↔ FastAPI ↔ OSC ↔ Ableton Live

A **mix** is an Ableton group track that contains at least one non-group child track. The group track's name is the mix name, its fader is the master output, and its child tracks are the mixer channels. Mixes can be nested inside an organizational parent group (e.g. a "Monitor" group) — the parent is excluded from mix detection because it only contains group children.

**Backend** (`server/`): FastAPI app with dependency injection via `injector`. `MixerService` holds business logic; `AbletonBridge` ABC abstracts OSC communication so tests can swap in an in-memory implementation.

**Frontend** (`ui/src/`): Svelte 5 with runes. Tailwind CSS v4 dark theme. Stores are `.svelte.js` files using module-level runes. In dev mode, Vite proxies `/ws` to the FastAPI server.

**Faux-solo** (`solo_manager.py`): Mutes sibling tracks instead of using Ableton's native solo, which would solo globally across all mixes. This is a core design decision — do not replace with native solo.

## Testing

**No mocking.** Backend tests use dependency injection with real alternative implementations (`InMemoryBridge` records commands in lists). Frontend tests use Vitest against pure functions in `helpers.js`.

Backend fixtures live in `tests/conftest.py` and `tests/factories.py`. Unit tests instantiate `MixerService` directly; integration tests use Starlette's `TestClient` with `websocket_connect()`.

## Maintenance

- **Keep tests current.** When changing behavior, update or add tests. Prefer clear test names over inline comments.
- **Keep README.md current.** When adding commands, changing setup, or altering structure, update README.md to match.
- **Keep this file current.** When you add new concepts, design decisions, or structural changes that a future Claude session would need to understand, update CLAUDE.md. Remove anything that has become stale. The goal is for this file to stay accurate and useful over time — not to document every file, but to capture what isn't obvious from reading the code.
