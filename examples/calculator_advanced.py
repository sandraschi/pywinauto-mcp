import asyncio
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


async def run_calculator_example():
    """
    Demonstrates advanced element tree traversal and interaction using the Windows Calculator.
    """
    print("--- Advanced Calculator Automation Example ---")

    # Logic flow simulated for MCP tools:

    # 1. Open Calculator
    print("[1] Opening Calculator (calc.exe)...")

    # 2. Wait for window and find elements
    # Tool: mcp_pywinauto_explorer(operation="list_elements", window_title="Calculator")
    print("[2] Extracting UI element tree...")

    # 3. Perform calculation (e.g., 2 + 2)
    # Tool: mcp_pywinauto_mouse(operation="click", element_name="Two")
    # Tool: mcp_pywinauto_mouse(operation="click", element_name="Plus")
    # Tool: mcp_pywinauto_mouse(operation="click", element_name="Two")
    # Tool: mcp_pywinauto_mouse(operation="click", element_name="Equals")
    print("[3] Clicking: '2', '+', '2', '='")

    # 4. Verify result
    # Tool: mcp_pywinauto_explorer(operation="get_element_text", element_name="CalculatorResults")
    print("[4] Verifying result is '4'...")

    print("\nCalculation simulation complete.")
    print("This demonstrates complex element identification across nested UI layers.")


if __name__ == "__main__":
    asyncio.run(run_calculator_example())
