# TODO: Replace AbletonOSC with a Vivo-owned Remote Script

## Why

AbletonOSC is a general-purpose OSC bridge exposing hundreds of Ableton API endpoints. Vivo uses 14 of them. The current setup clones the full repo at install time (`setup_abletonosc.py`), which is fragile and pulls in ~15 handler modules we don't need.

The goal: a single-file (or near-single-file) Remote Script checked into this repo that only implements the OSC addresses Vivo actually uses. No base classes, no handler framework — just a flat ControlSurface that wires up callbacks directly.

## What Vivo uses

The 14 OSC addresses sent by `server/bridge.py`:

- **Song**: `get/num_tracks`, `get/track_data` (bulk query for name, color, is_foldable, is_grouped, group_track, mute)
- **Track get/set**: `volume` (mixer_device property), `mute` (direct track property)
- **Track listeners**: `start_listen`/`stop_listen` for `volume`, `mute`, `output_meter_left`, `output_meter_right`

## Plan

### 1. Create `remote_script/`

A new top-level directory containing a minimal Ableton Remote Script. Rather than porting AbletonOSC's class hierarchy (Handler base class → SongHandler/TrackHandler subclasses), flatten everything into the ControlSurface subclass itself. The only pieces needed from AbletonOSC are:

- **`pythonosc/`** — copy as-is. Ableton's embedded Python has no pip, so this vendored OSC library must ship with the script.
- **The non-blocking UDP server** — AbletonOSC rolled its own (`osc_server.py`) because pythonosc's built-in server beachballs in Ableton's single-threaded runtime. This is the one file worth keeping mostly intact.
- **The ControlSurface** — a single class with `__init__` (bind OSC handlers, start tick loop), `tick` (poll socket), `disconnect` (remove listeners, close socket). All 14 OSC callbacks are methods or lambdas on this class. No inheritance hierarchy.

Key details:
- `volume` lives on `track.mixer_device`, not `track` directly — listeners use `add_value_listener`/`remove_value_listener` on the parameter object, not `add_volume_listener` on the track.
- `mute` and meter properties are direct track properties — listeners use `add_<prop>_listener`/`remove_<prop>_listener` on the track.
- Listener cleanup must track these two types separately to avoid errors on shutdown.
- `track_data` must handle `Live.Track.Track` values (e.g. `group_track`) by converting them to track indices.

### 2. Add Ableton API stubs for intellisense

The Remote Script imports `ableton.v2.control_surface` and `Live`, which only exist inside Ableton's Python runtime. Add type stubs as git submodules so editors can resolve these:

- Decompiled framework classes: https://github.com/gluon/AbletonLive12_MIDIRemoteScripts (`ableton/`, `_Framework/`)
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

## Future: Tauri

This project will eventually be packaged as a native desktop app via Tauri. Relevant implications for this task:

- The FastAPI server will become a sidecar process spawned by the Tauri app (or be replaced by a Rust backend using Tauri commands). The OSC protocol between server and Remote Script is the boundary between the two processes — changing how the UI is packaged doesn't affect the Remote Script. The protocol itself will grow as new features are added.
- The Tauri app can automate Remote Script installation (copy files to the Remote Scripts dir on first launch / update), so `setup_remote_script.py` should stay a simple, standalone copy operation that's easy to replicate from Rust.
- The Remote Script itself always runs inside Ableton regardless of how the UI is packaged.
