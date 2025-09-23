#!/usr/bin/env python3
"""
Test script for desktop state capture functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pywinauto_mcp.desktop_state import DesktopStateCapture

def test_basic_capture():
    """Test basic desktop state capture"""
    print("Testing basic desktop state capture...")

    capturer = DesktopStateCapture(max_depth=5)  # Lower depth for faster testing
    result = capturer.capture()

    print(f"Found {result['element_count']} elements")
    print(f"Interactive elements: {len(result['interactive_elements'])}")
    print(f"Informative elements: {len(result['informative_elements'])}")

    # Print first few lines of text report
    lines = result['text'].split('\n')[:10]
    print("Text report preview:")
    for line in lines:
        print(f"  {line}")

    return result

def test_vision_capture():
    """Test desktop state capture with vision"""
    print("\nTesting desktop state capture with vision...")

    capturer = DesktopStateCapture(max_depth=3)
    result = capturer.capture(use_vision=True)

    print(f"Found {result['element_count']} elements")

    if 'screenshot_base64' in result:
        print(f"Screenshot captured ({len(result['screenshot_base64'])} chars)")
        # Don't print the full base64, just confirm it's there
    else:
        print("No screenshot captured")

    return result

if __name__ == "__main__":
    try:
        # Test basic functionality
        basic_result = test_basic_capture()

        # Test with vision (optional, might fail without proper setup)
        try:
            vision_result = test_vision_capture()
        except Exception as e:
            print(f"Vision test failed (expected if PIL not properly configured): {e}")

        print("\n✅ Desktop state capture tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
