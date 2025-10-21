#!/usr/bin/env python3
"""
Script to remove description= parameters from @mcp.tool() decorators.

This converts old FastMCP patterns to FastMCP 2.12 compliance where
docstrings are the primary documentation source.
"""

import re
from pathlib import Path


def remove_description_param(file_path: Path) -> tuple[bool, str]:
    """Remove description parameter from @mcp.tool() decorator.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        Tuple of (modified: bool, message: str)
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Pattern 1: @mcp.tool(\n    description="""...""",\n)
    # Replace with: @mcp.tool
    pattern1 = r'@mcp\.tool\(\s*description=""".*?""",?\s*\)'
    content = re.sub(pattern1, '@mcp.tool', content, flags=re.DOTALL)
    
    # Pattern 2: @mcp.tool(\n    description="...",\n)
    # Replace with: @mcp.tool
    pattern2 = r'@mcp\.tool\(\s*description="[^"]*",?\s*\)'
    content = re.sub(pattern2, '@mcp.tool', content, flags=re.DOTALL)
    
    # Pattern 3: @mcp.tool("tool_name")
    # Keep as-is (this is for custom tool names)
    
    # Pattern 4: @mcp.tool(\n    description=...\n    name=...\n)
    # Replace with: @mcp.tool("name")
    pattern4 = r'@mcp\.tool\(\s*description=""".*?""",?\s*name="([^"]+)"\s*\)'
    content = re.sub(pattern4, r'@mcp.tool("\1")', content, flags=re.DOTALL)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return True, f"✅ Fixed {file_path.name}"
    
    return False, f"⏭️  Skipped {file_path.name} (no changes needed)"


def main():
    tools_dir = Path("src/advanced_memory/mcp/tools")
    
    print("🔧 Removing description= parameters from all tools...")
    print("=" * 60)
    
    modified_files = []
    skipped_files = []
    
    for tool_file in sorted(tools_dir.glob("*.py")):
        if tool_file.name == "__init__.py":
            continue
            
        modified, message = remove_description_param(tool_file)
        print(message)
        
        if modified:
            modified_files.append(tool_file.name)
        else:
            skipped_files.append(tool_file.name)
    
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Modified: {len(modified_files)} files")
    print(f"  Skipped: {len(skipped_files)} files")
    
    if modified_files:
        print(f"\n✅ Modified files:")
        for fname in sorted(modified_files):
            print(f"  - {fname}")
    
    print(f"\n🎯 All tools now FastMCP 2.12 compliant!")
    print(f"   (Docstrings are the primary documentation)")


if __name__ == "__main__":
    main()

