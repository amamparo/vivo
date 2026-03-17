# Live Ears

Web-based monitor mixer for Ableton Live. Each band member controls their own mix from their phone.

## How It Works

In Ableton, each monitor mix is a **group track** — the group name is the mix name, the group fader is the master output, and the child tracks are the mixer channels. Live Ears discovers these groups over OSC and presents them as selectable mixes via a mobile-friendly web UI.

```
Svelte UI ↔ WebSocket ↔ FastAPI ↔ OSC ↔ Ableton Live (LiveEarsOSC Remote Script)
```

Solo is "faux-solo" — it mutes sibling tracks rather than using Ableton's native solo, so soloing in one mix doesn't affect others.

## Prerequisites

- Python 3.13+ (via pyenv; see `.python-version`)
- [Poetry](https://python-poetry.org/)
- Node.js (via nvm; see `.nvmrc`)
- [just](https://github.com/casey/just) task runner
- Ableton Live 11+ (macOS)

## Setup

### 1. Install dependencies

```sh
nvm install
just install
```

### 2. Install LiveEarsOSC Remote Script

```sh
just setup
```

This copies `remote_script/` into Ableton's MIDI Remote Scripts directory (`~/Music/Ableton/User Library/Remote Scripts/LiveEarsOSC`).

### 3. Enable LiveEarsOSC in Ableton Live

1. Open Ableton Live
2. Go to **Preferences > Link, Tempo & MIDI**
3. Under **Control Surface**, select **LiveEarsOSC**
4. No MIDI input/output ports need to be selected

### 4. Build and run

```sh
just build
just run
```

Open `http://localhost:8000` on your phone (same Wi-Fi network).

## Development

```sh
just dev        # Server + UI with file-watching
just dev-server # FastAPI with auto-reload only
just dev-ui     # Vite dev server with HMR only
just test       # Run pytest + vitest suites
just check      # Run svelte-check + pyright
```

## Project Structure

```
remote_script/      Ableton Remote Script (LiveEarsOSC, installed via just setup)
src-tauri/          Tauri desktop app (system tray, sidecar management)
server/             Python backend (FastAPI + python-osc)
  app.py            App factory, WebSocket endpoint
  main.py           Entry point, DI wiring
  bridge.py         AbletonBridge ABC + OSC implementation
  mixer_service.py  Business logic
  solo_manager.py   Faux-solo state management
  models.py         Track dataclass, AbletonState
ui/                 Svelte 5 frontend (Tailwind CSS v4)
  src/lib/
    components/     Fader, MeterBar, ChannelStrip, etc.
    stores/         WebSocket connection, mixer state
    helpers.js      Volume scaling, dB conversion
    helpers.test.js Vitest suite for volume/meter math
tests/              Pytest suite (no mocking, uses DI)
logs/               Runtime logs (gitignored)
  server.log        FastAPI/uvicorn output
  ui.log            Vite dev server output
  liveearsosc.log   Ableton remote script output
```
