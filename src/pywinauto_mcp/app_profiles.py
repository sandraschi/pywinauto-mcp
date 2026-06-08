"""Per-application automation profiles — foreground policy, window title, regions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppProfile:
    app_id: str
    window_title: str
    dispatch: str = "foreground"
    keyboard_backend: str = "win32"
    description: str = ""


PROFILES: dict[str, AppProfile] = {
    "vroidstudio": AppProfile(
        app_id="vroidstudio",
        window_title="VRoid Studio",
        dispatch="foreground",
        keyboard_backend="win32",
        description="Unity GPU app — always foreground, shortcut-first",
    ),
    "vroid": AppProfile(
        app_id="vroidstudio",
        window_title="VRoid Studio",
        dispatch="foreground",
        keyboard_backend="win32",
    ),
    "libreoffice": AppProfile(
        app_id="libreoffice",
        window_title="LibreOffice",
        dispatch="background",
        keyboard_backend="pyautogui",
        description="Calc/Writer — background UIA often works",
    ),
}


def get_profile(app_id: str) -> AppProfile | None:
    return PROFILES.get(app_id.lower())


def list_profiles() -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for p in PROFILES.values():
        if p.app_id in seen:
            continue
        seen.add(p.app_id)
        out.append(
            {
                "app_id": p.app_id,
                "window_title": p.window_title,
                "dispatch": p.dispatch,
                "keyboard_backend": p.keyboard_backend,
                "description": p.description,
            }
        )
    return out
