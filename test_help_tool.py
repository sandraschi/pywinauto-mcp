#!/usr/bin/env python3
"""
Test script for the help tool functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pywinauto_mcp.tools.basic_tools import get_help

def test_help_overview():
    """Test basic help overview"""
    print("Testing help overview...")

    help_info = get_help()
    print(f"Server: {help_info['server']}")
    print(f"Total tools: {help_info['total_tools']}")
    print(f"Categories: {list(help_info['categories'].keys())}")
    print("\nGetting started:")
    for item in help_info['getting_started']:
        print(f"  - {item}")

    return help_info

def test_category_help():
    """Test category-specific help"""
    print("\nTesting category help...")

    categories = ['windows', 'desktop_state', 'system']
    for category in categories:
        try:
            help_info = get_help(category=category)
            if help_info['status'] == 'success':
                print(f"{category}: {len(help_info['tools'])} tools")
            else:
                print(f"{category}: {help_info['error']}")
        except Exception as e:
            print(f"{category}: Error - {e}")

def test_tool_details():
    """Test specific tool details"""
    print("\nTesting tool details...")

    tools = ['get_desktop_state', 'health_check', 'click_element']
    for tool in tools:
        try:
            help_info = get_help(tool_name=tool)
            if 'tool_details' in help_info:
                details = help_info['tool_details']
                print(f"{tool}: {details['description'][:50]}...")
            else:
                print(f"{tool}: {help_info.get('error', 'No details found')}")
        except Exception as e:
            print(f"{tool}: Error - {e}")

if __name__ == "__main__":
    try:
        test_help_overview()
        test_category_help()
        test_tool_details()
        print("\n✅ Help tool tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
