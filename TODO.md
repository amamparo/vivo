# TODO: Package Vivo as a Tauri Desktop App

## Why

Vivo currently runs as a dev-mode web stack (FastAPI + Vite). For a band to actually use it at a gig, someone has to open a terminal and run `just dev`. The goal: a single installable macOS app with a system tray icon that starts the server and shows its status — no terminal, no Python path wrangling.

## Architecture

```
┌─────────────────────────────────┐
│  Tauri App (Rust)               │
│  ┌───────────────┐              │
│  │ System Tray   │              │
│  │ - Server URL  │              │
│  │ - Start/Stop  │              │
│  │ - Quit        │              │
│  └───────┬───────┘              │
│          │ spawns                │
│  ┌───────▼───────────────────┐  │
│  │ FastAPI Sidecar           │  │
│  │ (bundled Python + server) │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
         ▲ OSC (UDP 11000/11001)
         │
   Ableton Live (VivOSC Remote Script)

Band members connect via phone browser → http://<host>:8000
```

The Tauri app is **not** wrapping the UI in a webview. The Svelte UI is served by FastAPI to phones over the local network — same as today. The Tauri app is purely a host process: system tray icon, sidecar lifecycle management, and Remote Script installation.

## Plan

### 1. Tauri project scaffolding

Initialize Tauri inside the existing repo. Since we're not using a webview for the UI (the Svelte app is served to phones by FastAPI), the Tauri "frontend" is essentially unused — the app is tray-only with no window.

- `npm create tauri-app` or `cargo tauri init` in a new `src-tauri/` directory
- Configure `tauri.conf.json`:
  - No default window (tray-only app)
  - Bundle identifier: `com.vivo.mixer`
  - macOS minimum version, app icon, etc.
- Add system tray with menu: server URL (click to copy), Start/Stop, Quit
- Tray icon reflects server state (running/stopped/error)

### 2. Bundle FastAPI as a sidecar

Tauri's [sidecar](https://tauri.app/develop/sidecar/) feature can spawn and manage external binaries. Package the Python server as a standalone executable:

- Use PyInstaller or PyOxidizer to bundle `server/` + dependencies into a single binary
- Register it as a Tauri sidecar in `tauri.conf.json`
- The Rust side spawns the sidecar on launch, monitors its stdout/stderr, and kills it on quit
- Embed the built Svelte UI (`ui/dist/`) inside the sidecar bundle so FastAPI serves it directly — no separate static file path needed at runtime

Key details:
- The sidecar binary must include `python-osc`, `fastapi`, `uvicorn`, and `injector`
- Port selection: default to 8000, but detect conflicts and pick an open port
- Sidecar stdout should include the bound port so the tray can display the URL
- Graceful shutdown: Tauri sends a signal, sidecar cleans up OSC listeners before exiting

### 3. Auto-install Remote Script

On every app startup, ensure the installed VivOSC Remote Script matches the version bundled with the app. This replaces the manual `just setup` step entirely.

- Add a `VERSION` constant to `remote_script/__init__.py` (e.g. `__version__ = "0.2.0+a1b2c3"`)
- **Dev builds** (`just setup`): version includes a randomly generated hash suffix (e.g. `0.2.0-dev+f7a3b1`), regenerated on each build — so every `just setup` always copies, matching the "code is changing constantly" reality of development
- **Release builds**: version is stable (e.g. `0.2.0`) — only triggers a copy when the app is actually updated
- On startup, read the installed `__init__.py` version and compare to the bundled version
- If versions differ (or VivOSC isn't installed at all), copy the bundled remote script
- If the version matches, skip — no unnecessary disk writes
- Log the outcome either way (installed, updated from X→Y, or already up to date)

This means: installing/updating the app automatically installs/updates the Remote Script. The user only needs to select VivOSC as a control surface once in Ableton preferences.

For development, `just setup` always copies (due to the random hash) — no need to think about whether the installed version is stale.

### 4. System tray implementation

The tray menu is the entire "server-side UI":

- **Status line**: "Serving on http://192.168.x.x:8000" (local network IP, not localhost)
- **Copy URL**: copies the serve URL to clipboard (for sharing with band members)
- **Start / Stop**: toggle the sidecar process
- **Quit**: stop sidecar, exit app

Nice-to-haves for later:
- Show connected client count
- Auto-start on login (launchd plist)
- Notification when Ableton connection is lost

### 5. Build & distribution

- `just build-app` — builds the Svelte UI, bundles the Python sidecar, then `cargo tauri build`
- Output: `.dmg` installer for macOS
- Signing/notarization can come later

### 6. Development workflow

Keep the current `just dev` workflow intact for development. The Tauri app is a packaging/distribution concern — day-to-day development still uses `just dev` with hot reload. Add:

- `just dev-tauri` — runs the Tauri app in dev mode (tray + sidecar with auto-reload)
- `just build-app` — full production build

## Open questions

- **PyInstaller vs PyOxidizer vs Nuitka** for bundling the Python server — need to evaluate which produces the smallest/most reliable macOS binary with FastAPI + uvicorn
- **Code signing** — needed for macOS distribution outside the App Store. Requires an Apple Developer account ($99/year). Can defer this.
- **Windows/Linux** — Tauri supports all three, but Ableton's Remote Script path differs per OS. Start macOS-only, generalize later.
- **Auto-update** — Tauri has built-in updater support. Worth adding once there's a distribution channel.
