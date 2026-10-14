"""Anonymous usage counting: how many people open, scan with and clean with the app.

Privacy rules, enforced by code and by tests/test_telemetry.py:
  * Nothing is ever sent while STATS_URL is empty, so a build without an endpoint is fully offline.
  * Only the five fields in `payload()` are sent. Nothing read from Zalo folders (names, paths,
    counts, sizes, chat ids) can reach this module: it takes an event name and nothing else.
  * The install id is random, created on this machine, and deleted when the user turns counting off.
  * Sending runs on a background thread with a short timeout; failures are ignored silently.
"""

from __future__ import annotations

import json
import os
import platform
import secrets
import sys
import threading
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

# Set by the release build (or ZCLEANER_STATS_URL while testing). Empty = counting is unavailable.
STATS_URL = ""

# Fixed vocabulary. Milestones are counted once per install; app_open on every launch.
EVENTS = frozenset({"app_open", "scan_done", "first_clean"})
ONCE_ONLY = frozenset({"scan_done", "first_clean"})
TIMEOUT_SECONDS = 3


def app_version() -> str:
    from . import __version__
    return __version__


def coarse_os() -> str:
    """Operating system and major version only, e.g. 'macOS 15' or 'Windows 11'."""
    if sys.platform == "darwin":
        return "macOS " + (platform.mac_ver()[0].split(".")[0] or "?")
    if sys.platform == "win32":
        return "Windows " + platform.release()
    return "Linux"


def allowed_endpoint(url: str) -> bool:
    """HTTPS only (plain HTTP just to loopback, for tests): nobody can read the signal in transit."""
    parts = urlparse(url or "")
    if parts.scheme == "https" and parts.hostname:
        return True
    return parts.scheme == "http" and parts.hostname in {"127.0.0.1", "localhost"}


def _post(url: str, payload: dict) -> None:
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "ZCleaner"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS):
        pass


class Telemetry:
    def __init__(self, state_file: Path, url: str | None = None, sender=_post, background: bool = True):
        self.state_file = Path(state_file)
        self.url = (os.environ.get("ZCLEANER_STATS_URL") or STATS_URL) if url is None else url
        self._sender = sender
        self._background = background
        self._lock = threading.Lock()

    # --- state ---------------------------------------------------------
    @property
    def available(self) -> bool:
        return allowed_endpoint(self.url)

    def _load(self) -> dict:
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _save(self, data: dict) -> None:
        from .server import write_private_json  # imported lazily: server imports this module
        write_private_json(self.state_file, data)

    @property
    def enabled(self) -> bool:
        """On by default; the user can turn it off on the welcome screen or in Settings."""
        return self._load().get("enabled", True) is not False

    def set_enabled(self, value: bool) -> None:
        with self._lock:
            if value:
                self._save({**self._load(), "enabled": True})
            else:
                # Turning it off forgets who this install was.
                self._save({"enabled": False})

    # --- sending -------------------------------------------------------
    def payload(self, event: str, install_id: str) -> dict:
        return {"id": install_id, "event": event, "app": app_version(), "os": coarse_os(),
                "arch": platform.machine()}

    def event(self, name: str) -> bool:
        """Record one of the fixed events. Returns True if a signal was handed to the sender."""
        if name not in EVENTS or not self.available:
            return False
        with self._lock:
            state = self._load()
            if state.get("enabled", True) is False:
                return False
            done = state.get("done", [])
            if name in ONCE_ONLY and name in done:
                return False
            install_id = state.get("id")
            if not (isinstance(install_id, str) and len(install_id) == 32):
                install_id = secrets.token_hex(16)
            state.update(enabled=True, id=install_id)
            if name in ONCE_ONLY:
                state["done"] = done + [name]
            try:
                self._save(state)
            except OSError:
                return False
            body = self.payload(name, install_id)
        if self._background:
            threading.Thread(target=self._send, args=(body,), name="zc-stats", daemon=True).start()
        else:
            self._send(body)
        return True

    def _send(self, body: dict) -> None:
        try:
            self._sender(self.url, body)
        except Exception:
            pass  # counting must never affect the app
