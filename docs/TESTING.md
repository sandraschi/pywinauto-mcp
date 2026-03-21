# Testing (CI vs local)

Aligned with **mcp-central-docs** → `standards/testing-environment-aware.md` (clone sibling repo **mcp-central-docs**).

## Fleet context

**pywinauto-mcp** is the **implemented** variant for **local Windows + OpenCV / USB cameras** (hardware-marked tests skip in CI). Central docs describe the same pattern and **fleet intent**: roll the drop-in scaffold into **all other repos** that touch **hardware** — IP or UVC **cameras**, **robots**, **scanners**, **vacuums**, **smart home / IoT**, and similar — shared **markers** and **hooks**, with **device-specific fixtures** per repo.

## What this repo does

| Location | Behavior |
|----------|----------|
| **GitHub Actions / `CI=true`** | No real Windows desktop, no OpenCV cameras. Tests marked `requires_hardware` or `destructive` are **skipped**. Prefer **mocks** and **HTTP** (`TestClient`) tests. |
| **Local Windows** | You can run real desktop / camera probes. Opt in to heavy suites with env vars (e.g. `PYWINAUTO_TEST_REAL_WINDOWS=1` for Notepad window tests). |

## Markers

Defined in `tests/conftest_env.py` and `[tool.pytest.ini_options]` in `pyproject.toml`.

- **`requires_hardware`** — Opens real OpenCV devices or host-only code paths. **Skipped in CI.**
- **`destructive`** — Drives real UI (e.g. Notepad tests). **Skipped in CI**; locally also needs `PYWINAUTO_TEST_REAL_WINDOWS=1` where documented.
- **`requires_network`** — LAN-dependent; skipped in CI.
- **`ci_only`** — Runs when `CI=true`; skipped on typical local runs.

## Commands

```powershell
# Same as CI: hardware tests skipped
$env:CI = "true"; uv run pytest tests/ -q

# Local: include hardware-marked tests (needs Windows + devices as applicable)
uv run pytest tests/ -q

# Only hardware-marked tests
uv run pytest tests/ -m requires_hardware -q
```

## Camera API

- **`tests/test_cameras_api.py`** — `test_cameras_get_returns_json` mocks `enumerate_cameras` (CI-safe).
- **`test_enumerate_cameras_runs_on_local_host`** is marked **`requires_hardware`** (skipped in CI).
