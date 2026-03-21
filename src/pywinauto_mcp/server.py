"""ASGI entry: REST API (`/api/v1/...`) + FastMCP streamable HTTP (`/mcp`).

Uvicorn target: ``pywinauto_mcp.server:app``
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pywinauto_mcp.api import api_router
from pywinauto_mcp.app import app as mcp_app

# FastMCP HTTP app only registers ``/mcp``; mount it after REST routes so ``/api/v1/*`` resolves.
_mcp_http = mcp_app.http_app()

app = FastAPI(title="pywinauto-mcp", version="0.3.2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10788",
        "http://localhost:10788",
        "http://127.0.0.1:10706",
        "http://localhost:10706",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.mount("/", _mcp_http)
