"""ASGI entry point for uvicorn (web_sota backend)."""

from pywinauto_mcp.app import app as mcp_app

app = mcp_app.http_app()
