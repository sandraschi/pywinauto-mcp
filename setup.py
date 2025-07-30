#!/usr/bin/env python3
"""
Setup script for PyWinAutoMCP package.

This script allows installing the package with pip for development:
    pip install -e .
"""
from setuptools import setup, find_packages
import os

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from pyproject.toml
with open("pyproject.toml", "r", encoding="utf-8") as f:
    pyproject_content = f.read()

# Extract dependencies (simplified - for a more robust solution, use tomli)
import re

def extract_dependencies():
    """Extract dependencies from pyproject.toml."""
    deps_section = re.search(r'^dependencies\s*=\s*\[(.*?)\]', 
                           pyproject_content, 
                           re.DOTALL | re.MULTILINE)
    if not deps_section:
        return []
    
    # Parse dependencies, handling multi-line and comments
    deps = []
    for line in deps_section.group(1).split('\n'):
        line = line.strip().strip(',').strip()
        if not line or line.startswith('#'):
            continue
        # Remove quotes and any trailing comments
        dep = line.strip('"\'').split('#')[0].strip()
        if dep and not dep.startswith('['):  # Skip any remaining section headers
            deps.append(dep)
    return deps

setup(
    name="pywinauto-mcp",
    version="0.2.0",
    author="Sandra Schilling",
    author_email="sandra@example.com",
    description="FastMCP server for Windows UI automation using PyWinAuto",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pywinauto-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=extract_dependencies(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration",
    ],
    entry_points={
        "console_scripts": [
            "pywinauto-mcp=pywinauto_mcp.main:main",
        ],
        "fastmcp.plugins": [
            "pywinauto=pywinauto_mcp.plugins:setup_plugin",
        ],
    },
)
