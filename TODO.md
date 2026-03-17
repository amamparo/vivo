# TODO: Replace AbletonOSC with a Vivo-owned Remote Script

## Why

AbletonOSC is a general-purpose OSC bridge exposing hundreds of Ableton API endpoints. Vivo uses 14 of them. The current setup clones the full repo at install time (`setup_abletonosc.py`), which is fragile and pulls in ~15 handler modules we don't need.

The goal: a minimal Remote Script checked into this repo that only implements the OSC addresses Vivo actually uses.

## What Vivo uses

The 14 OSC addresses sent by `server/bridge.py`:

- **Song**: `get/num_tracks`, `get/track_data` (bulk query for name, color, is_foldable, is_grouped, group_track, mute)
- **Track get/set**: `volume` (mixer_device property), `mute` (direct track property)
- **Track listeners**: `start_listen`/`stop_listen` for `volume`, `mute`, `output_meter_left`, `output_meter_right`

## Plan

### 1. Create `remote_script/`

A new top-level directory containing a complete Ableton Remote Script. Port from AbletonOSC:

- The OSC server (`osc_server.py`) — non-blocking UDP socket, message dispatch. Can drop wildcard address matching.
- The base handler (`handler.py`) — `_get_property`, `_set_property`, `_start_listen`, `_stop_listen`. Can drop `_call_method`.
- The manager (`manager.py`) — ControlSurface subclass with tick loop. Can drop reload_imports, MIDI mapping, log-level-via-OSC.
- A song handler — only `num_tracks` and `track_data`.
- A track handler — volume/mute get/set, listeners for volume/mute/meters. Note: volume lives on `track.mixer_device`, not `track` directly, so it needs separate get/set/listen methods from mute. The mixer listener cleanup path must be separate from the base handler's `_clear_listeners` to avoid a KeyError on shutdown (the original AbletonOSC has this bug too).
- Copy `AbletonOSC/pythonosc/` as-is — Ableton's embedded Python has no pip, so this vendored OSC library must ship with the script.

### 2. Add Ableton API stubs for intellisense

The Remote Script imports `ableton.v2.control_surface` and `Live`, which only exist inside Ableton's Python runtime. Add type stubs (e.g. as git submodules) so editors can resolve these:

- Decompiled framework classes: https://github.com/gluon/AbletonLive11_MIDIRemoteScripts (`ableton/`, `_Framework/`)
- Live API stubs: https://github.com/cylab/AbletonLive-API-Stub (`Live/`)

Point Pylance at them via `.vscode/settings.json` `python.analysis.extraPaths`. Wire `git submodule update --init` into `just install` so they're fetched automatically.

### 3. Replace setup script

Replace `setup_abletonosc.py` with a script that copies `remote_script/` into Ableton's Remote Scripts directory (no git clone). Update `just setup`, README, and CLAUDE.md references.

### 4. Clean up

- Delete `AbletonOSC/` and its `.gitignore` entry
- Delete `setup_abletonosc.py`
- Update README setup instructions and architecture diagram
- Run `just test` to verify nothing broke (server tests don't touch the Remote Script)
- Manual test: `just setup`, select the new Control Surface in Ableton, `just dev`, verify tracks/volume/meters/mute/solo all work
