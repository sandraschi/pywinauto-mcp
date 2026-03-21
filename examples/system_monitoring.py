import asyncio
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


async def run_system_monitor_example():
    """
    Demonstrates background process interaction and system tray monitoring.
    """
    print("--- System Monitoring & Tray Interaction Example ---")

    # Logic flow simulated for MCP tools:

    # 1. Monitor active processes
    # Tool: mcp_pywinauto_process_mgr(operation="list_processes", top_n=5)
    print("[1] Auditing top 5 CPU consuming windows...")

    # 2. Check for hidden or system tray icons
    # Tool: mcp_pywinauto_explorer(operation="list_tray_icons")
    print("[2] Listing active system tray icons...")

    # 3. Interact with a background app (e.g., Steam or Discord)
    # Tool: mcp_pywinauto_window_mgr(operation="restore", window_title="Discord")
    print("[3] Restoring Discord from tray...")

    print("\nSystem monitoring logic completed.")
    print("Useful for health-checks and automated environment setup.")


if __name__ == "__main__":
    asyncio.run(run_system_monitor_example())
