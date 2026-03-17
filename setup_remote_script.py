"""Install the VivOSC Remote Script into Ableton Live's Remote Scripts directory.

Dev builds stamp a random hash into __version__ so every `just setup` copies fresh.
Release builds use the version from remote_script/__init__.py as-is.
"""

import re
import secrets
import shutil
from pathlib import Path

ABLETON_REMOTE_SCRIPTS = Path.home() / "Music" / "Ableton" / "User Library" / "Remote Scripts"
PROJECT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = PROJECT_DIR / "remote_script"
TARGET_DIR = ABLETON_REMOTE_SCRIPTS / "VivOSC"

IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "pyrightconfig.json")

VERSION_RE = re.compile(r'^__version__\s*=\s*["\'](.+?)["\']', re.MULTILINE)


def read_version(init_path: Path) -> str | None:
    """Extract __version__ from an __init__.py file."""
    if not init_path.exists():
        return None
    match = VERSION_RE.search(init_path.read_text())
    return match.group(1) if match else None


def stamp_dev_version(init_path: Path) -> str:
    """Rewrite __version__ in-place with a random dev hash suffix."""
    text = init_path.read_text()
    match = VERSION_RE.search(text)
    if not match:
        return "unknown"
    base = match.group(1).split("+")[0]  # strip any existing hash
    dev_version = f"{base}+{secrets.token_hex(3)}"
    new_text = text[:match.start(1)] + dev_version + text[match.end(1):]
    init_path.write_text(new_text)
    return dev_version


def install(dev: bool = True) -> None:
    ABLETON_REMOTE_SCRIPTS.mkdir(parents=True, exist_ok=True)

    # Read the source version (before stamping)
    source_init = SOURCE_DIR / "__init__.py"
    installed_version = read_version(TARGET_DIR / "__init__.py")

    if dev:
        # Stamp a unique dev hash so version always differs
        new_version = stamp_dev_version(source_init)
    else:
        new_version = read_version(source_init) or "unknown"

    if installed_version == new_version:
        print(f"VivOSC {installed_version} already up to date — skipping install")
        return

    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)

    shutil.copytree(SOURCE_DIR, TARGET_DIR, ignore=IGNORE)

    # Write config so the remote script logs to the project's logs/ directory
    log_dir = PROJECT_DIR / "logs"
    (TARGET_DIR / "_config.py").write_text(f'LOG_DIR = {str(log_dir)!r}\n')

    if installed_version:
        print(f"\nVivOSC updated: {installed_version} → {new_version}")
    else:
        print(f"\nVivOSC {new_version} installed to: {TARGET_DIR}")
    print(f"Logs will write to: {log_dir}")

    if not installed_version:
        print("\nNext steps:")
        print("  1. Restart Ableton Live")
        print("  2. Go to Preferences > Link, Tempo & MIDI")
        print('  3. Under Control Surface, select "VivOSC"')
        print("  4. No input/output MIDI ports need to be selected")


def main():
    install(dev=True)


if __name__ == "__main__":
    main()
