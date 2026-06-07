# automation_assert — Specification

## Purpose

First-class UI verification for computer-use automation. Replaces ad-hoc SHA256 polling in consumer repos (vroidstudio-mcp `AutomationEngine._wait_stable`) with a shared, region-aware assert tool.

## Tool surface

**MCP tool name:** `automation_assert`

**Pattern:** Portmanteau — single tool, `operation` enum (matches `automation_visual`, `automation_mouse`, etc.).

## Operations

### `hash`

Compute fingerprint of an image file or live capture.

| Param | Type | Description |
|-------|------|-------------|
| `image_path` | str? | Existing PNG/JPG. If omitted, capture live. |
| `window_handle` | int? | HWND for live capture |
| `region_*` | int? | Crop region (screen coords or window-relative) |
| `hash_algorithm` | `sha256` \| `dhash` | Default `dhash` (tolerates minor rendering noise) |

**Returns:** `{hash, algorithm, width, height}`

### `hash_region`

Alias of `hash` with required `region_*`. Documents intent: hash only the editor canvas, ignore chrome.

### `diff`

Compare two images.

| Param | Type | Description |
|-------|------|-------------|
| `image_path` | str | Image A (before) |
| `image_path_b` | str | Image B (after) |
| `region_*` | int? | Optional crop applied to both |
| `change_threshold_pct` | float | Pixel change sensitivity (default 1.0) |
| `output_path` | str? | Save heatmap/diff PNG |

**Returns:** `{changed_pct, pixels_changed, total_pixels, diff_path, sizes_match}`

### `wait_stable`

Poll captures until hash is unchanged for N consecutive frames.

| Param | Type | Description |
|-------|------|-------------|
| `window_handle` | int? | Target window |
| `image_path` | str? | Static image path (testing only) |
| `region_*` | int? | Region to monitor |
| `stable_frames_required` | int | Default 2 |
| `poll_interval_s` | float | Default 0.5 |
| `timeout_s` | float | Default 10.0 |
| `hash_algorithm` | str | Default `dhash` |

**Returns:** `{stable: true, frames_observed, final_hash, screenshot_path}`

On timeout: `status="error"` with last hash and partial capture path.

### `assert_changed`

Fail if before/after are too similar.

| Param | Type | Description |
|-------|------|-------------|
| `image_path` | str | Before |
| `image_path_b` | str | After |
| `change_threshold_pct` | float | Min change required (default 1.0) |
| `region_*` | int? | Optional crop |

**Returns:** `status="success"` if changed enough; `status="error"` with `changed_pct` if not.

### `assert_unchanged`

Fail if before/after differ beyond threshold.

| Param | Type | Description |
|-------|------|-------------|
| `image_path` | str | Before |
| `image_path_b` | str | After |
| `unchanged_threshold_pct` | float | Max allowed change (default 0.5) |

### `assert_template`

OpenCV template match — "is this dialog visible?"

| Param | Type | Description |
|-------|------|-------------|
| `image_path` | str? | Haystack image (or live capture) |
| `template_path` | str | Needle template PNG |
| `window_handle` | int? | Live capture source |
| `match_threshold` | float | 0–1, default 0.8 |
| `region_*` | int? | Search region |

**Returns:** `{found: bool, confidence, center_x, center_y}`

### `assert_text`

OCR region and check for expected substring.

| Param | Type | Description |
|-------|------|-------------|
| `image_path` | str? | Source image |
| `window_handle` | int? | Live capture |
| `expected_text` | str | Text to find |
| `exact_match` | bool | Default false (substring) |
| `region_*` | int? | OCR region |

**Returns:** `{found: bool, ocr_text}`

Requires Tesseract (same as `automation_visual.extract_text`).

## Implementation

| Module | Role |
|--------|------|
| `assert_engine.py` | Pure functions: capture, hash, diff, stable poll, template, OCR assert |
| `portmanteau_assert.py` | MCP tool registration |
| `models.py` | `AssertOperationRequest` Pydantic model |

## Hash algorithms

- **sha256:** Exact byte hash. Fast, zero tolerance. Good for file integrity, bad for GPU-rendered UI.
- **dhash:** 64-bit difference hash. Hamming distance ≤ 5 treated as "same" for stable detection. Better for Unity/VRoid rendering noise.

## Error contract

All operations return `ToolResult`:

```python
ToolResult(
    status="success" | "error",
    message="human summary",
    data={...},
    recovery_tip="actionable hint for agent",
)
```

Assert failures use `status="error"` (not exception) so agents can read `data.changed_pct` and retry.

## Consumer migration (vroidstudio-mcp)

Replace local `_wait_stable` / `_verify_change`:

```python
# before (vroidstudio)
await self._wait_stable(step_name)
await self._verify_change(before, after, step)

# after (via cua-mcp)
await call_pywinauto_tool("automation_assert", {
    "request": {
        "operation": "wait_stable",
        "window_handle": self._handle,
        "timeout_s": 10,
    }
})
await call_pywinauto_tool("automation_assert", {
    "request": {
        "operation": "assert_changed",
        "image_path": str(before),
        "image_path_b": str(after),
        "change_threshold_pct": 1.0,
    }
})
```

## Why dhash over sha256

vroidstudio-mcp originally used full-frame SHA256 in `_wait_stable`. Problems:

- Unity/GPU rendering produces pixel noise between frames → false "changed"
- Loading spinners and status bar clocks → false "unchanged" never reached
- Full-frame hash includes window chrome → irrelevant churn

**dhash** (difference hash) with Hamming distance ≤ 5 treats near-identical frames as stable. Combine with `region_*` to monitor only the editor canvas.

## Future: evidence bundles (Phase 9)

On assert failure, optionally return:

```json
{
  "before_path": "...",
  "after_path": "...",
  "diff_path": "...",
  "changed_pct": 0.3,
  "recovery_tip": "Call automation_windows(focus) before retry."
}
```

Host LLM reviews images; cua-mcp does not run vision models server-side.

## Tests

Unit tests use synthetic PIL images in `tmp_path` — no Windows GUI required for hash/diff/assert_changed/unchanged/wait_stable on static files.

16 tests in `tests/test_automation_assert.py` (15 pass; `assert_text` skips if Tesseract binary not in PATH).
