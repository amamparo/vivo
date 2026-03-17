"""Install the VivOSC Remote Script into Ableton Live's Remote Scripts directory."""

import shutil
from pathlib import Path

ABLETON_REMOTE_SCRIPTS = Path.home() / "Music" / "Ableton" / "User Library" / "Remote Scripts"
SOURCE_DIR = Path(__file__).resolve().parent / "remote_script"
TARGET_DIR = ABLETON_REMOTE_SCRIPTS / "VivOSC"


def main():
    ABLETON_REMOTE_SCRIPTS.mkdir(parents=True, exist_ok=True)

    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)

    shutil.copytree(SOURCE_DIR, TARGET_DIR, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    print(f"\nVivOSC installed to: {TARGET_DIR}")
    print("\nNext steps:")
    print("  1. Restart Ableton Live")
    print("  2. Go to Preferences > Link, Tempo & MIDI")
    print('  3. Under Control Surface, select "VivOSC"')
    print("  4. No input/output MIDI ports need to be selected")


if __name__ == "__main__":
    main()
