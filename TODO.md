# Vivo

Write a python web-server that serves a web-based mixer for Ableton Live.

## User Experience

* The intended user of the web interface is a band member who wishes to control their own monitor mix from their mobile device.
* The landing page is a list menu that shows all of the available mixes.
* Upon clicking on a mix, the user should be presented with a mobile-responsive mixer showing all of the tracks in their mix as well as the master track.
* Controls for each track:
  * level fader
    * custom vertical range slider (0 to 1, step 0.002) with quartic volume scaling for a natural audio feel
    * unity gain tick mark at ~70.71%
    * double-tap to reset to unity gain
    * dB readout displayed below the fader
    * distinguish between taps and drags using a movement threshold
    * large variant for the master output fader
  * peak level meter
    * stereo (L/R) vertical peak meter per channel
    * green-to-yellow-to-red gradient color zones
    * red clip indicator when signal exceeds 0dB
    * smooth CSS transitions (~100ms) for visual responsiveness
  * mute
  * solo (see `note on solo` below)
    * the required project setup is such that each band member's mix is comprised of tracks nested together in a group. as such, just utilizing the built-in solo buttons will not work, because soloing a track in a band member's mix would solo that track across the entire ableton project. instead, we need to be a little clever. when soloing a track in a monitor mix, we should achieve this by muting all other tracks within the same monitor group. If I solo a second track, then just unmute that track (leaving two tracks un-muted in the group). If I have one track solo'ed, and then I un-solo that track, then all tracks should become un-muted. I think this complex faux-solo state should be tracked within the server's python code.
    * when any channel is soloed, non-soloed channels should have reduced opacity to visually indicate they are inactive
    * the server must remember pre-solo mute states so they can be restored when exiting solo mode
* the UI/look and feel should be identical to the more-me interface in this repo: https://github.com/amamparo/reaper-web-controllers
  * dark theme: near-black background (#0a0a0a), light gray text (#a9abab / text-neutral-400)
  * each track displays a colored dot indicator derived from its Ableton track color
  * toggle buttons (solo/mute): red (bg-red-600) when active, dark neutral (bg-neutral-800) when inactive
  * faders: dark inset track with a metallic/beveled gradient knob
  * touch-optimized: 44px minimum touch targets, disabled text selection, no tap highlight, no overscroll bounce
* mixer layout:
  * header bar with back arrow and the selected mix name
  * "Master Output" section with a large vertical fader
  * horizontally scrollable row of channel strip cards, each containing: colored dot + track name, solo/mute buttons, volume fader, stereo peak meter

## Ableton Interfacing

* utilize AbletonOSC (https://github.com/ideoforms/AbletonOSC) — a MIDI Remote Script that exposes an OSC API for controlling Ableton Live
  * the python server communicates with Ableton via OSC messages using the python-osc library
  * AbletonOSC runs within Ableton as a control surface and listens for OSC commands (default port 11000, replies on 11001)
* provide a setup script that copies AbletonOSC's Remote Script files to Ableton's MIDI Remote Scripts directory
* in the README, include setup steps for:
  * running the setup script
  * enabling the AbletonOSC control surface in Live's Preferences > Link, Tempo & MIDI

## Real-time Communication

* the Svelte frontend communicates with the FastAPI server over WebSockets for low-latency bidirectional updates
  * client → server: fader moves, mute/solo toggles
  * server → client: meter levels, track state changes, track list updates
* the FastAPI server communicates with Ableton via OSC (python-osc)
  * server → Ableton: volume/mute commands via OSC
  * Ableton → server: meter levels, track state via OSC listener

## Technical Implementation Requirements

* python
  * use version 3.13.11 (per .python-version)
  * use poetry for dependency management
  * use FastAPI as the web framework (with uvicorn)
  * use python-osc for OSC communication with AbletonOSC
  * use websockets support built into FastAPI (via starlette)
* UI
  * utilize Svelte 5 (with runes: $state, $derived, $effect, $props)
  * utilize Tailwind CSS for styling (dark theme, minimal custom CSS)
  * build the Svelte app with Vite; serve the built static files from FastAPI
* misc
  * use the "just" task runner tool for scripts (check, lint, run, install, setup, etc)
