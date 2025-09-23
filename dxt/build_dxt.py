"""
Build script for creating PyWinAutoMCP DXT package.
"""
import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any

def load_manifest() -> Dict[str, Any]:
    """Load and validate the DXT manifest."""
    manifest_path = Path(__file__).parent / "dxt_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Basic validation
    required_fields = ["name", "version", "description", "server"]
    for field in required_fields:
        if field not in manifest:
            raise ValueError(f"Missing required field in manifest: {field}")
    
    return manifest

def create_dxt_structure(version: str, build_dir: Path) -> Path:
    """Create the DXT package directory structure."""
    # Create build directory
    build_dir = build_dir / f"pywinauto-mcp-{version}"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Create required directories
    (build_dir / "server").mkdir(parents=True)
    return build_dir

def copy_source_files(build_dir: Path) -> None:
    """Copy required source files to the build directory."""
    # Get the parent directory (where the dxt folder is located)
    parent_dir = Path(__file__).parent.parent
    src_dir = parent_dir / "src"
    target_dir = None

    # Look for directories starting with pywinauto_mcp
    for item in src_dir.iterdir():
        if item.is_dir() and item.name.startswith("pywinauto_mcp"):
            target_dir = item
            break

    if target_dir is None:
        raise FileNotFoundError(f"pywinauto_mcp source directory not found in {src_dir}")

    print(f"Found source directory: {target_dir}")

    # Copy package files
    shutil.copytree(target_dir, build_dir / "server" / target_dir.name)
    
    # Copy requirements.txt
    requirements = parent_dir / "requirements.txt"
    if requirements.exists():
        shutil.copy2(requirements, build_dir / "requirements.txt")

    # Copy README and LICENSE if they exist
    for f in ["README.md", "LICENSE"]:
        file_path = parent_dir / f
        if file_path.exists():
            shutil.copy2(file_path, build_dir / f)

def create_zip_archive(build_dir: Path, version: str, parent_dir: Path) -> Path:
    """Create a zip archive of the DXT package."""
    dist_dir = parent_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    zip_path = dist_dir / f"pywinauto-mcp-{version}.dxt"
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname)
    
    return zip_path

def main() -> None:
    """Main function to build the DXT package."""
    try:
        # Get the parent directory (where the dxt folder is located)
        parent_dir = Path(__file__).parent.parent

        # Load and validate manifest
        manifest = load_manifest()
        version = manifest["version"]

        print(f"Building PyWinAutoMCP DXT package v{version}")

        # Create build directory
        build_root = parent_dir / "build"
        build_root.mkdir(exist_ok=True)
        build_dir = create_dxt_structure(version, build_root)
        
        # Copy source files
        print("Copying source files...")
        copy_source_files(build_dir)

        # Copy manifest
        shutil.copy2(Path(__file__).parent / "dxt_manifest.json", build_dir / "manifest.json")

        # Create ZIP archive
        print("Creating DXT package...")
        zip_path = create_zip_archive(build_dir, version, parent_dir)
        
        print(f"\n✅ DXT package created successfully: {zip_path}")
        print(f"   Size: {zip_path.stat().st_size / (1024 * 1024):.2f} MB")
        
    except Exception as e:
        print(f"\n❌ Error building DXT package: {e}")
        raise

if __name__ == "__main__":
    main()
