"""Install the VivOSC Remote Script into Ableton Live's Remote Scripts directory."""

import shutil
from pathlib import Path

ABLETON_REMOTE_SCRIPTS = Path.home() / "Music" / "Ableton" / "User Library" / "Remote Scripts"
PROJECT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = PROJECT_DIR / "remote_script"
TARGET_DIR = ABLETON_REMOTE_SCRIPTS / "VivOSC"


def main():
    ABLETON_REMOTE_SCRIPTS.mkdir(parents=True, exist_ok=True)

    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)

    shutil.copytree(SOURCE_DIR, TARGET_DIR, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pyrightconfig.json"))

    # Write config so the remote script logs to the project's logs/ directory
    log_dir = PROJECT_DIR / "logs"
    config = TARGET_DIR / "_config.py"
    config.write_text(f'LOG_DIR = {str(log_dir)!r}\n')

    print(f"\nVivOSC installed to: {TARGET_DIR}")
    print(f"Logs will write to:  {log_dir}")
    print("\nNext steps:")
    print("  1. Restart Ableton Live")
    print("  2. Go to Preferences > Link, Tempo & MIDI")
    print('  3. Under Control Surface, select "VivOSC"')
    print("  4. No input/output MIDI ports need to be selected")


if __name__ == "__main__":
    main()
