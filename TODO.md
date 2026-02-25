# Vivo

Write a python web-server that serves a web-based mixer for Ableton Live.

## User Experience

* The intended user of the web interface is a band member who wishes to control their own monitor mix from their mobile device.
* The landing page is a list menu that shows all of the available mixes.
* Upon clicking on a mix, the user should be presented with a mobile-responsive mixer showing all of the tracks in their mix as well as the master track.
* Controls for each track:
  * level fader
  * mute
  * solo (see `note on solo` below)
    * the required project setup is such that each band member's mix is comprised of tracks nested together in a group. as such, just utilizing the built-in solo buttons will not work, because soloing a track in a band member's mix would solo that track across the entire ableton project. instead, we need to be a little clever. when soloing a track in a monitor mix, we should achieve this by muting all other tracks within the same monitor group. If I solo a second track, then just unmute that track (leaving two tracks un-muted in the group). If I have one track solo'ed, and then I un-solo that track, then all tracks should become un-muted. I think this complex faux-solo state should be tracked within the server's python code.
* the UI/look and feel should be identical to the more-me interface in this repo: https://github.com/amamparo/reaper-web-controllers

## Ableton interfacing

* utilize Ableton OSC
* provide a control surface program (I think that's what this it's called), as well as a setup script that copies the relevant files to Ableton's control surfaces dir
* in the README, include in the setup steps the detail about running the aforementioned setup script as well as how to enable the control surface in Live's preferences

## Technical Implementation Requirements
* python
  * use the version in .python-version
  * use poetry for dependency management
  * use a lightweight server framework that also has good support for serving UIs
* UI
  * utilize svelte.js
  * utilize tailwind for an elegant UI with minimal custom CSS
* misc
  * use the "just" task runner tool for scripts (check, lint, run, install, setup, etc)

