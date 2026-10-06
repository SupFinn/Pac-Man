import sys
from pathlib import Path


def resource_path(relative: str) -> str:
    """Return the absolute path of a bundled resource.

    Works from the source folder and from a PyInstaller build.
    """
    base = getattr(sys, "_MEIPASS", None)
    root = Path(base) if base else Path(__file__).resolve().parents[2]
    return str(root / relative)


def user_data_path(filename: str) -> str:
    """Return a writable path for user data in the home folder."""
    return str(Path.home() / ".pacman" / filename)
