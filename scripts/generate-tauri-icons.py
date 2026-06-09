"""Generate minimal Tauri icon set from a solid-color PNG (requires Pillow)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "web_sota" / "src-tauri" / "icons"


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    base = Image.new("RGBA", (512, 512), (30, 58, 138, 255))
    png_path = ICON_DIR / "icon.png"
    base.save(png_path)
    # ICO with common sizes for Windows installer
    ico_path = ICON_DIR / "icon.ico"
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.resize((256, 256)).save(
        ico_path,
        format="ICO",
        sizes=[(s[0], s[1]) for s in sizes],
    )
    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")


if __name__ == "__main__":
    main()
