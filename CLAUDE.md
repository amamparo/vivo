# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
just install        # Create .venv, poetry install, npm install
just build          # Build Svelte UI to ui/dist
just run            # Serve on :8000 (requires built UI)
just dev            # Server + UI with file-watching
just dev-server     # FastAPI with auto-reload only
just dev-ui         # Vite dev server with HMR only
just test           # Run pytest + vitest suites
just check          # Run svelte-check
just setup          # Install AbletonOSC Remote Script into Ableton
```

Run a single Python test: `just test -- tests/test_solo_manager.py::TestSoloManager::test_soloing_a_track_mutes_all_others`
Run UI tests only: `cd ui && npm test`
Run a single UI test: `cd ui && npx vitest run -t "test name"`

Poetry requires a workaround due to pyenv: the justfile sets `VIRTUAL_ENV` and `PATH` explicitly. Use `just` commands rather than bare `poetry run`.

## Logs

`just dev`, `just dev-ui`, and `just run` write output to `logs/server.log` and `logs/ui.log` (gitignored). Read these files to diagnose runtime errors.

## Architecture

**Communication chain:** Svelte UI ↔ WebSocket ↔ FastAPI ↔ OSC ↔ Ableton Live

A **mix** is an Ableton group track that contains at least one non-group child track. The group track's name is the mix name, its fader is the master output, and its child tracks are the mixer channels. Mixes can be nested inside an organizational parent group (e.g. a "Monitor" group) — the parent is excluded from mix detection because it only contains group children.

### Backend (`server/`)

- **app.py** — `create_app(container: injector.Injector) -> FastAPI` factory. WebSocket endpoint at `/ws`, background loops for meter polling (50ms) and track refresh (5s).
- **main.py** — Entry point. Wires `ProductionModule` (binds `AbletonOSCBridge`) and creates the app. Uvicorn target: `server.main:app`.
- **mixer_service.py** — `MixerService` holds all business logic. Injected with `AbletonState`, `SoloManager`, `AbletonBridge`.
- **bridge.py** — `AbletonBridge` ABC defines the interface (`set_volume`, `set_mute`, `start_listeners`, `stop_all_listeners`, `startup`, `shutdown`, `refresh_tracks`). `AbletonOSCBridge` is the real implementation using python-osc (send port 11000, listen port 11001).
- **solo_manager.py** — Faux-solo: mutes sibling tracks instead of using Ableton's native solo (which would solo globally across all mixes). Snapshots pre-solo mute states on first solo, restores them when the last solo is toggled off.
- **models.py** — `Track` dataclass and `AbletonState` (track storage with `get_mix_tracks()` and `get_children(group_index)`).

### Frontend (`ui/src/`)

Svelte 5 with runes (`$state`, `$derived`, `$effect`, `$props`). Tailwind CSS v4 dark theme (`#0a0a0a` bg, `text-neutral-400`). Stores are in `.svelte.js` files using module-level runes.

- **stores/connection.svelte.js** — WebSocket client with auto-reconnect.
- **stores/mixer.svelte.js** — Reactive state for mixes, tracks, meters. Exports functions (`selectMix`, `setVolume`, `toggleSolo`, etc.) that send WebSocket messages.
- **components/Fader.svelte** — Vertical range slider with quartic volume scaling (`vol = pos^4 * 4`), tap-vs-drag detection, double-tap reset to unity (70.71% position). Pseudo-element thumb styling requires custom CSS; all other styling uses Tailwind.

### WebSocket Protocol

Client → server: `select_mix`, `set_volume`, `set_mute`, `toggle_solo`, `request_mix_state`
Server → client: `mixes`, `mix_state`, `meters`

## Testing

**No mocking.** Backend tests use dependency injection with real alternative implementations. Frontend tests use Vitest against pure functions.

### Backend (`tests/`)

- `tests/factories.py` — `InMemoryBridge` (records commands in lists instead of sending OSC) and `make_track()` factory.
- `tests/conftest.py` — `TestModule` binds `InMemoryBridge` via injector. Fixtures: `container`, `state`, `bridge`, `app`.
- Unit tests instantiate `MixerService` directly with `InMemoryBridge`. Integration tests use Starlette's `TestClient` with `websocket_connect()`.

### Frontend (`ui/src/lib/`)

- `helpers.test.js` — Tests for volume scaling, dB conversion, meter math, and round-trip consistency.
- All testable math (volume curves, dB conversion, meter level-to-percent) lives in `helpers.js` as pure functions.

## Maintenance Rules

- **Keep tests current.** When changing backend behavior, update or add tests to cover the change. Tests should describe what the code does — prefer clear test names over inline comments.
- **Keep README.md current.** When adding commands, changing setup steps, or altering project structure, update README.md to match.
