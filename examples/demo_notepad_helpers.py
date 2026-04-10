"""Shared helpers for Notepad demos (DPI, temp files, find window by title)."""

from __future__ import annotations

import ctypes
import logging
import os
import re
import tempfile
import time

from pywinauto import Desktop

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception as e:
        logger.debug("SetProcessDPIAware: %s", e)


def notepad_exe() -> str:
    return os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "notepad.exe")


def make_temp_demo_files(prefix: str, count: int) -> tuple[str, list[str]]:
    """Create empty ``prefix_N.txt`` files; return (directory, basenames)."""
    tmp = tempfile.mkdtemp(prefix="pywinauto_demo_")
    names: list[str] = []
    for i in range(count):
        base = f"{prefix}_{i}.txt"
        path = os.path.join(tmp, base)
        with open(path, "wb"):
            pass
        names.append(base)
    return tmp, names


def wait_for_notepad_title(basename: str, *, timeout: float = 25.0, poll: float = 0.2) -> int | None:
    """Return HWND of a top-level window whose title contains ``basename``."""
    needle = basename.lower()
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        desktop = Desktop(backend="uia")
        for w in desktop.windows():
            try:
                t = (w.window_text() or "").lower()
                if needle in t and ("notepad" in t or "记事本" in t):
                    return int(w.handle)
            except Exception as e:
                logger.debug("window skip: %s", e)
                continue
        time.sleep(poll)
    return None


_GRID_TITLE_RE = re.compile(r"PyDemoGrid(\d+)", re.I)


def collect_cmd_grid_windows(want: int = 9, *, timeout: float = 40.0, poll: float = 0.35) -> dict[int, int]:
    """Wait for top-level windows titled ``PyDemoGrid0`` … ``PyDemoGrid{want-1}``.

    Returns ``{ index: hwnd }`` (may be incomplete if consoles open slowly or host uses one terminal tab).
    """
    deadline = time.perf_counter() + timeout
    got: dict[int, int] = {}
    while time.perf_counter() < deadline and len(got) < want:
        desktop = Desktop(backend="uia")
        for w in desktop.windows():
            try:
                title = w.window_text() or ""
                m = _GRID_TITLE_RE.search(title)
                if m is None:
                    continue
                idx = int(m.group(1))
                if 0 <= idx < want and idx not in got:
                    got[idx] = int(w.handle)
            except Exception as e:
                logger.debug("enum skip: %s", e)
                continue
        time.sleep(poll)
    return got
