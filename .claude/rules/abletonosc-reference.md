# AbletonOSC Protocol Reference

This rule provides context for extending the Live Ears Remote Script's OSC interface.

## Background

Live Ears includes a custom Ableton Remote Script (in `remote_script/`) derived from
[AbletonOSC](https://github.com/ideoforms/AbletonOSC) by ideoforms. It implements
a small subset of OSC addresses. When adding new OSC commands, follow the conventions below.

## OSC address conventions

Addresses follow the Live Object Model hierarchy:

```
/live/<object>/<action>/<property>
```

- **Objects**: `song`, `track`, `clip`, `clip_slot`, `device`, `scene`, `view`, `application`
- **Actions**: `get`, `set`, `start_listen`, `stop_listen`, or method names directly
- **Track-level addresses** take `track_index` as the first param (or `*` for all tracks)
- **Mixer properties** (volume, panning, sends) live on `track.mixer_device`, not `track` directly

## Ports

- **11000**: Remote Script listens (incoming commands)
- **11001**: Remote Script sends (responses and listener updates)

## Listener pattern

`start_listen` registers a Live API listener that fires on property changes. Responses
are sent to `/live/<object>/get/<property>` with `(index, value)`. `stop_listen` removes it.
The handler immediately sends the current value on registration.

## Currently implemented addresses

See `server/bridge.py` for the addresses Live Ears sends, and `remote_script/` for the
handlers. Currently: `song/get/num_tracks`, `song/get/track_data`, and track-level
`volume`, `mute`, `output_meter_left`, `output_meter_right` (get/set/listen).

## Full AbletonOSC API reference

The complete catalog of available OSC addresses (for reference when adding new ones)
is in the AbletonOSC README: https://github.com/ideoforms/AbletonOSC/blob/master/README.md

Key categories and commonly needed addresses:

### Song

| Address | Params | Description |
|---|---|---|
| `/live/song/get/num_tracks` | — | Returns track count |
| `/live/song/get/track_data` | min, max, ...properties | Bulk query: `track.name`, `track.color`, `track.is_foldable`, `track.is_grouped`, `track.group_track`, `track.mute`, etc. |
| `/live/song/get/track_names` | [min, max] | Returns track names |
| `/live/song/get/num_scenes` | — | Returns scene count |
| `/live/song/start_playing` | — | Start playback |
| `/live/song/stop_playing` | — | Stop playback |
| `/live/song/get/tempo` | — | Query tempo |
| `/live/song/set/tempo` | tempo | Set tempo |
| `/live/song/get/is_playing` | — | Query playback state |

### Track

Track addresses take `track_index` (or `*`) as first param.

| Address | Extra params | Description |
|---|---|---|
| `/live/track/get/volume` | — | Query volume (mixer_device property, 0.0–1.0) |
| `/live/track/set/volume` | value | Set volume |
| `/live/track/get/mute` | — | Query mute state |
| `/live/track/set/mute` | value | Set mute (0/1) |
| `/live/track/get/solo` | — | Query solo state |
| `/live/track/set/solo` | value | Set solo (0/1) |
| `/live/track/get/arm` | — | Query arm state |
| `/live/track/set/arm` | value | Set arm (0/1) |
| `/live/track/get/panning` | — | Query pan (-1.0 to 1.0) |
| `/live/track/set/panning` | value | Set pan |
| `/live/track/get/send` | send_index | Query send level |
| `/live/track/set/send` | send_index, value | Set send level |
| `/live/track/get/name` | — | Query track name |
| `/live/track/set/name` | name | Set track name |
| `/live/track/get/color` | — | Query track color |
| `/live/track/set/color` | color | Set track color |
| `/live/track/get/output_meter_left` | — | Left channel meter level |
| `/live/track/get/output_meter_right` | — | Right channel meter level |
| `/live/track/get/output_meter_level` | — | Combined meter level |
| `/live/track/get/is_foldable` | — | Whether track is a group |
| `/live/track/get/is_grouped` | — | Whether track is inside a group |
| `/live/track/get/fold_state` | — | Group fold state |
| `/live/track/set/fold_state` | value | Set group fold state |

All gettable properties support `start_listen`/`stop_listen` variants.

### Clip

Clip addresses take `track_index, clip_index` as first two params.

| Address | Extra params | Description |
|---|---|---|
| `/live/clip/fire` | — | Fire clip |
| `/live/clip/stop` | — | Stop clip |
| `/live/clip/get/name` | — | Query clip name |
| `/live/clip/get/length` | — | Query clip length |
| `/live/clip/get/is_playing` | — | Query playing state |
| `/live/clip_slot/fire` | — | Fire clip slot |

### Device

Device addresses take `track_index, device_index` as first two params.

| Address | Extra params | Description |
|---|---|---|
| `/live/device/get/name` | — | Device name |
| `/live/device/get/parameters/value` | — | All parameter values |
| `/live/device/set/parameter/value` | param_index, value | Set a parameter |

## Ableton Live Object Model (LOM)

The OSC addresses map to properties/methods on Live API objects. When implementing
new handlers, refer to the LOM documentation for available properties:

- **LOM reference (Cycling '74)**: https://docs.cycling74.com/apiref/lom/
- **Python API docs (Live 11)**: https://structure-void.com/PythonLiveAPI_documentation/Live11.0.xml

Key object hierarchy: `Song` → `Track[]` → `ClipSlot[]` → `Clip`, and
`Track` → `MixerDevice` → `volume`/`panning`/`sends[]`.
