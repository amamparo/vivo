"""Setup script to install AbletonOSC Remote Script into Ableton Live's MIDI Remote Scripts directory."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ABLETON_REMOTE_SCRIPTS = Path.home() / "Music" / "Ableton" / "User Library" / "Remote Scripts"
ABLETONOSC_REPO = "https://github.com/ideoforms/AbletonOSC.git"
CLONE_DIR = Path(__file__).resolve().parent / "AbletonOSC"
TARGET_DIR = ABLETON_REMOTE_SCRIPTS / "AbletonOSC"


def main():
    # Clone or update AbletonOSC repo
    if CLONE_DIR.exists():
        print(f"AbletonOSC already cloned at {CLONE_DIR}, pulling latest...")
        subprocess.run(["git", "-C", str(CLONE_DIR), "pull"], check=True)
    else:
        print(f"Cloning AbletonOSC to {CLONE_DIR}...")
        subprocess.run(["git", "clone", ABLETONOSC_REPO, str(CLONE_DIR)], check=True)

    # Find the Remote Script source directory
    source_dir = CLONE_DIR / "abletonosc"
    if not source_dir.exists():
        print(f"Error: Expected source directory not found at {source_dir}")
        sys.exit(1)

    # Create Ableton Remote Scripts directory if needed
    ABLETON_REMOTE_SCRIPTS.mkdir(parents=True, exist_ok=True)

    # Copy the Remote Script files
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)

    # AbletonOSC expects the whole repo as the Remote Script
    # Copy the relevant files
    shutil.copytree(CLONE_DIR, TARGET_DIR, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "client", "docs", "tests"))

    print(f"\nAbletonOSC installed to: {TARGET_DIR}")
    print("\nNext steps:")
    print("  1. Restart Ableton Live")
    print("  2. Go to Preferences > Link, Tempo & MIDI")
    print('  3. Under Control Surface, select "AbletonOSC"')
    print("  4. No input/output MIDI ports need to be selected")


if __name__ == "__main__":
    main()
