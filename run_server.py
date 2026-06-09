"""PyInstaller entrypoint for pywinauto-mcp HTTP sidecar (Tauri externalBin)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(sys._MEIPASS)
    sys.path.insert(0, str(base / "src"))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

os.environ.setdefault("MCP_TRANSPORT", "http")

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("PYWINAUTO_MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("PYWINAUTO_MCP_PORT", os.environ.get("MCP_PORT", "10789")))
    log_level = os.environ.get("PYWINAUTO_MCP_LOG_LEVEL", "info")
    uvicorn.run(
        "pywinauto_mcp.server:app",
        host=host,
        port=port,
        log_level=log_level,
    )
