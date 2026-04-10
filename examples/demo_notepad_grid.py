"""Launch nine windows and tile them in a 3x3 grid.

Default: nine **cmd.exe** consoles (``CREATE_NEW_CONSOLE``), titled ``PyDemoGrid0`` … ``PyDemoGrid8``.
That is reliable on Windows 11, where **Notepad** often merges new files into **one** process/tabs,
so launcher PIDs do not match top-level HWNDs.

Optional ``--use-notepad``: open nine empty temp ``.txt`` files in Notepad and match by window title
(best effort; may yield fewer than nine windows if your Notepad uses a single tabbed window).

Run: ``uv run python examples/demo_notepad_grid.py``
"""

from __future__ import annotations

import argparse
import ctypes
import sys
from pathlib import Path

_EXAMPLES_DIR = str(Path(__file__).resolve().parent)
if _EXAMPLES_DIR not in sys.path:
    sys.path.insert(0, _EXAMPLES_DIR)

import logging
import os
import subprocess
import time

from pywinauto import Desktop
from pywinauto.findwindows import WindowNotFoundError

from demo_notepad_helpers import (
    collect_cmd_grid_windows,
    make_temp_demo_files,
    notepad_exe,
    wait_for_notepad_title,
)

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32
WM_CLOSE = 0x0010
SW_RESTORE = 9

CREATE_NEW_CONSOLE = getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010)


def _screen_size() -> tuple[int, int]:
    return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def _move_window_hwnd(hwnd: int, x: int, y: int, w: int, h: int) -> bool:
    """Resize/move any top-level HWND (cmd consoles are not always UIA-wrappable)."""
    user32.ShowWindow(hwnd, SW_RESTORE)
    return bool(user32.MoveWindow(hwnd, int(x), int(y), int(w), int(h), True))


def _close_hwnd(desktop: Desktop, hwnd: int) -> None:
    try:
        desktop.window(handle=hwnd).close()
    except Exception as e:
        logger.debug("close uia failed %s: %s", hwnd, e)
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)


def _cmd_exe() -> str:
    return os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "cmd.exe")


def _launch_cmd_grid() -> None:
    print("Starting 9 cmd.exe windows (PyDemoGrid0…8)…")
    cmd = _cmd_exe()
    for i in range(9):
        # Each process gets its own console window when CREATE_NEW_CONSOLE is set.
        subprocess.Popen(  # noqa: S603
            [cmd, "/k", f"title PyDemoGrid{i}"],
            creationflags=CREATE_NEW_CONSOLE,
            shell=False,
        )
        time.sleep(0.35)
        print(f"  [{i + 1}/9] started")


def _launch_notepad_grid() -> tuple[list[str], list[str]]:
    """Return (temp_dir, basenames) after launching one Notepad per file."""
    tmp, basenames = make_temp_demo_files("demo_grid", 9)
    np = notepad_exe()
    print("Starting 9 Notepad windows (one temp .txt each)…")
    for i, base in enumerate(basenames):
        path = os.path.join(tmp, base)
        subprocess.Popen([np, path], shell=False)  # noqa: S603
        time.sleep(0.35)
        print(f"  [{i + 1}/9] {base}")
    return tmp, basenames


def main() -> None:
    parser = argparse.ArgumentParser(description="Nine windows in a 3x3 grid.")
    parser.add_argument(
        "--gap",
        type=int,
        default=8,
        help="Pixels between tiles (default 8).",
    )
    parser.add_argument(
        "--no-close",
        action="store_true",
        help="Do not close windows when the script exits.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Non-interactive: show the grid for --dwell seconds, then exit (e.g. just demo).",
    )
    parser.add_argument(
        "--dwell",
        type=float,
        default=5.0,
        help="Seconds to keep the grid visible when --auto (default 5).",
    )
    parser.add_argument(
        "--use-notepad",
        action="store_true",
        help="Use Notepad + temp files instead of cmd (may find fewer than 9 on tabbed Notepad).",
    )
    args = parser.parse_args()

    if args.use_notepad:
        _launch_notepad_grid()
        time.sleep(1.5)
        handles_ordered: list[int] = []
        for i in range(9):
            base = f"demo_grid_{i}.txt"
            print(f"Locating window for {base!r}…")
            h = wait_for_notepad_title(base, timeout=20.0)
            if h is None:
                print(f"Warning: no window for {base}", file=sys.stderr)
            else:
                handles_ordered.append(h)
        if len(handles_ordered) < 9:
            print(
                f"Note: only found {len(handles_ordered)}/9 Notepad windows "
                "(Windows 11 often uses one tabbed window). Use default cmd grid for a full 3x3.",
                file=sys.stderr,
            )
    else:
        _launch_cmd_grid()
        time.sleep(1.0)
        by_idx = collect_cmd_grid_windows(want=9, timeout=45.0)
        if len(by_idx) < 9:
            print(
                f"Warning: only found {len(by_idx)}/9 console windows "
                "(check default terminal profile; Windows Terminal may tab into one window).",
                file=sys.stderr,
            )
        handles_ordered = [by_idx[i] for i in range(9) if i in by_idx]

    if not handles_ordered:
        print("No windows to tile.", file=sys.stderr)
        sys.exit(1)

    desktop = Desktop(backend="uia")
    sw, sh = _screen_size()
    gap = max(0, args.gap)
    bottom_reserve = 48
    usable_h = sh - bottom_reserve
    margin = 10
    cols, rows = 3, 3
    # Tile in a grid up to 3x3; with fewer windows, still use row-major slots
    cell_w = (sw - 2 * margin - gap * (cols - 1)) // cols
    cell_h = (usable_h - 2 * margin - gap * (rows - 1)) // rows

    closed: list[int] = []
    for idx, hwnd in enumerate(handles_ordered):
        row, col = divmod(idx, 3)
        if row >= 3:
            break
        x = margin + col * (cell_w + gap)
        y = margin + row * (cell_h + gap)
        try:
            if _move_window_hwnd(hwnd, x, y, cell_w, cell_h):
                closed.append(hwnd)
                print(f"Tile {idx + 1}: ({x}, {y}) size {cell_w}x{cell_h} hwnd={hwnd}")
            else:
                print(f"Warning: MoveWindow failed for hwnd {hwnd}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: position failed for hwnd {hwnd}: {e}", file=sys.stderr)

    if args.auto:
        print(f"\nGrid ready (auto). Holding for {args.dwell}s…")
        time.sleep(max(0.0, args.dwell))
    else:
        print("\nGrid ready. Press Enter to finish" + ("" if args.no_close else " (windows will close)…"))
        try:
            input()
        except EOFError:
            pass

    if not args.no_close and closed:
        print("Closing tiled windows…")
        for h in closed:
            try:
                _close_hwnd(desktop, h)
            except WindowNotFoundError:
                pass
            except Exception as e:
                logger.debug("close %s: %s", h, e)
        time.sleep(0.3)

    print("Done.")


if __name__ == "__main__":
    main()
