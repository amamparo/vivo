# TODO: Inline AbletonOSC Remote Script

Replace the cloned AbletonOSC repo with a minimal, Vivo-specific Remote Script that only handles the OSC messages we actually use.

## Context

AbletonOSC is a general-purpose OSC bridge with handlers for songs, tracks, clips, devices, scenes, views, and MIDI mapping. Vivo uses ~14 OSC addresses out of hundreds. The full repo is cloned at build time by `setup_abletonosc.py` and copied into Ableton's Remote Scripts directory.

The goal is to vendor a stripped-down Remote Script directly in this repo (no git clone step) that only implements what Vivo needs.

## OSC addresses Vivo actually uses

From `server/bridge.py`:

| Address | Purpose |
|---|---|
| `/live/song/get/num_tracks` | Track count |
| `/live/song/get/track_data` | Bulk track metadata (name, color, is_foldable, is_grouped, group_track, mute) |
| `/live/track/get/volume` | Query volume |
| `/live/track/set/volume` | Set volume |
| `/live/track/get/mute` | Query mute |
| `/live/track/set/mute` | Set mute |
| `/live/track/start_listen/volume` | Subscribe to volume changes |
| `/live/track/stop_listen/volume` | Unsubscribe |
| `/live/track/start_listen/mute` | Subscribe to mute changes |
| `/live/track/stop_listen/mute` | Unsubscribe |
| `/live/track/start_listen/output_meter_left` | Subscribe to left meter |
| `/live/track/stop_listen/output_meter_left` | Unsubscribe |
| `/live/track/start_listen/output_meter_right` | Subscribe to right meter |
| `/live/track/stop_listen/output_meter_right` | Unsubscribe |

## Steps

### 1. Create `remote_script/` directory

New top-level directory that will be installed as the Ableton Remote Script. Structure:

```
remote_script/
├── __init__.py              # create_instance() entry point
├── manager.py               # ControlSurface subclass (tick loop, init/shutdown)
├── osc_server.py            # OSC send/receive over UDP (from AbletonOSC)
├── handler.py               # Base handler with _get_property, _set_property, _start_listen, _stop_listen
├── song_handler.py          # Only: get/num_tracks, get/track_data
├── track_handler.py         # Only: get/set volume+mute, start/stop_listen for volume+mute+meters
├── constants.py             # OSC_LISTEN_PORT, OSC_RESPONSE_PORT
└── pythonosc/               # Vendored pythonosc (required — Ableton's Python has no pip)
    └── (copy from AbletonOSC/pythonosc/)
```

### 2. Port the core infrastructure

Copy and simplify from AbletonOSC:

- **`osc_server.py`** — Keep as-is, it's the non-blocking UDP socket server. Remove wildcard (`*`) address matching if we don't use it.
- **`handler.py`** — Keep `_get_property`, `_set_property`, `_start_listen`, `_stop_listen`, `_clear_listeners`. Remove `_call_method` (unused).
- **`manager.py`** — Simplify from AbletonOSC's version: only init `SongHandler` and `TrackHandler`. Remove reload_imports, MIDI mapping, log level OSC commands. Keep the tick loop, logging, and shutdown.
- **`__init__.py`** — `create_instance(c_instance)` entry point.
- **`pythonosc/`** — Copy the entire directory as-is (it's a vendored dependency that Ableton needs at runtime).

### 3. Port the handlers

- **`song_handler.py`** — Only implement:
  - `/live/song/get/num_tracks` — `lambda _: (len(self.song.tracks),)`
  - `/live/song/get/track_data` — The bulk query function (supports `track.name`, `track.color`, `track.is_foldable`, `track.is_grouped`, `track.group_track`, `track.mute`)

- **`track_handler.py`** — Only implement:
  - `get/set` for `mute` (direct track property)
  - `get/set` for `volume` (mixer_device property — needs the `_get_mixer_property`/`_set_mixer_property`/`_start_mixer_listen`/`_stop_mixer_listen` methods)
  - `start_listen/stop_listen` for `volume`, `mute`, `output_meter_left`, `output_meter_right`
  - Keep the `create_track_callback` wrapper that handles track index routing and `*` wildcard

### 4. Update `setup_abletonosc.py` → `setup_remote_script.py`

- Remove the git clone step entirely
- Copy `remote_script/` to Ableton's Remote Scripts directory (as `VivOSC` or similar name)
- Update the Control Surface name in the setup instructions

### 5. Update `justfile`

- `just setup` should call the new setup script
- Remove any reference to cloning AbletonOSC

### 6. Clean up

- Delete `AbletonOSC/` directory (or remove from `.gitignore` / `.gitmodules` if tracked)
- Update `README.md` setup instructions (no more "clones AbletonOSC" step)
- Update `CLAUDE.md` if the architecture description references AbletonOSC

### 7. Test

- Run `just setup` and verify the Remote Script appears in Ableton's Remote Scripts directory
- Select the new Control Surface in Ableton preferences
- Run `just dev` and verify the full communication chain still works (track listing, volume control, meters, mute/solo)
