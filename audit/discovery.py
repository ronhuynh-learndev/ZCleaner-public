"""Find likely Zalo media folders for the current OS user."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Mapping


def candidate_bases(home: Path, system: str, env: Mapping[str, str]) -> list[Path]:
    """Return narrow Zalo-owned directories, never broad home or AppData roots."""
    if system == "win32":
        roaming = Path(env.get("APPDATA", home / "AppData" / "Roaming"))
        local = Path(env.get("LOCALAPPDATA", home / "AppData" / "Local"))
        return [roaming / "ZaloData", roaming / "ZaloPC", local / "ZaloData", local / "ZaloPC"]
    if system == "darwin":
        support = home / "Library" / "Application Support"
        return [support / "ZaloData", support / "ZaloPC"]
    return []


def find_downloads(base: Path, max_depth: int = 5) -> list[Path]:
    """Search only inside a known Zalo directory, stopping at media folders."""
    if not base.is_dir() or base.is_symlink():
        return []
    found: list[Path] = []
    for folder, children, _ in os.walk(base, followlinks=False):
        current = Path(folder)
        depth = len(current.relative_to(base).parts)
        children[:] = [name for name in children if not name.startswith(".") and not (current / name).is_symlink()]
        if current.name == "ZaloDownloads":
            found.append(current)
            children.clear()
        elif depth >= max_depth:
            children.clear()
    return found


def request_folder_access(home: Path | None = None) -> str:
    """List the one macOS-protected folder we read, so the system permission box appears the moment a scan starts.

    macOS asks only when a folder's contents are listed, never for a plain existence check.
    Returns "ok", "denied" (the person said no) or "none" (nothing there to ask about).
    """
    home = home or Path.home()
    try:
        path = home / "Documents" / "Zalo Received Files"
        if path.is_symlink() or not path.is_dir():
            return "none"
        with os.scandir(path) as entries:
            next(entries, None)
        return "ok"
    except PermissionError:
        return "denied"
    except OSError:
        return "none"


def discover_roots(
    home: Path | None = None,
    system: str | None = None,
    env: Mapping[str, str] | None = None,
    extra: list[Path] | None = None,
) -> list[Path]:
    """Discover Zalo's media and received-file folders for this OS account."""
    home = home or Path.home()
    system = system or sys.platform
    env = env if env is not None else os.environ
    candidates: list[Path] = []
    for base in candidate_bases(home, system, env):
        candidates.extend(find_downloads(base))
    candidates.append(home / "Documents" / "Zalo Received Files")
    candidates.extend(extra or [])
    seen: set[Path] = set()
    roots: list[Path] = []
    for path in candidates:
        try:
            if not path.is_dir() or path.is_symlink():
                continue
        except OSError:  # a folder macOS won't let us look at is simply not a root
            continue
        real = path.resolve()
        if real not in seen:
            seen.add(real)
            roots.append(real)
    return roots


def state_directory(home: Path | None = None, system: str | None = None, env: Mapping[str, str] | None = None) -> Path:
    home = home or Path.home()
    system = system or sys.platform
    env = env if env is not None else os.environ
    if env.get("ZALO_CLEANER_STATE_DIR"):
        return Path(env["ZALO_CLEANER_STATE_DIR"]).expanduser()
    if system == "win32":
        return Path(env.get("LOCALAPPDATA", home / "AppData" / "Local")) / "ZaloCleaner"
    if system == "darwin":
        return home / "Library" / "Application Support" / "ZaloCleaner"
    return home / ".local" / "state" / "zalo-cleaner"
