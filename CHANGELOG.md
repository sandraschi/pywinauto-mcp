# 📋 Changelog

All notable changes to PyWinAuto MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Biometrics → `automation_face`:** Web UI calls **`POST /api/v1/tools/call`** for **list / capture & match / delete** when the tool is registered (`web_sota` helper `lib/mcpTools.ts`).
- **REST `GET /api/v1/safety/status`:** Same payload as MCP **`automation_safety("status")`** (webapp biometrics).
- **ASGI composite server:** FastAPI **`/api/v1/*`** (REST) + FastMCP HTTP **`/mcp`** — `pywinauto_mcp.server:app` for uvicorn; CORS for `web_sota`.
- **web_sota `/chat` — local LLM:** OpenAI-compatible proxy (`/api/v1/llm/*`) to **Ollama** / **LM Studio** on localhost only (SSRF-safe localhost); model list, **personas**, **prompt refiner**, optional **repo knowledge** from `llm_repo_context.py`. Env: **`PYWINAUTO_LLM_BASE_URL`**.
- **Camera enumeration:** `GET /api/v1/cameras/` probes OpenCV indices; **Biometrics** + **Tools** (`camera_index` for `automation_face`) show a **dropdown when multiple cameras** exist; `localStorage` sync. Env: **`PYWINAUTO_MCP_CAMERA_MAX_INDEX`** (default 10).
- **Environment-aware pytest** (aligned with **mcp-central-docs** `testing-environment-aware.md`): `tests/conftest_env.py`, markers (`requires_hardware`, `destructive`, …), **`docs/TESTING.md`** (fleet context), **`[tool.pytest.ini_options]`**; **`tests/test_cameras_api.py`**; real-window class marked for CI skip.
- **Docs:** **`docs/PRD.md`** refreshed (web stack, REST, LLM, testing); **`docs/README.md`** index; **`docs/TESTING.md`**; **`docs/LLM_REPO_CONTEXT.md`** pointer; camera notes in **`docs/SAFETY.md`** §5.

### Changed
- **`web_sota`:** Removed legacy **robotics teleop** (`/control`) and **Unity/3D placeholder** (`/visualizer`). **Biometrics** now has a **live browser webcam preview** (2D pan/zoom/rotate) plus **live safety** from **`/api/v1/safety/status`**. Fleet catalog entry **robotics-mcp** clarified (not this server).
- **`automation_face` is opt-in at runtime:** set **`PYWINAUTO_MCP_ENABLE_FACE=1`** and install the **`face`** extra; otherwise the tool is not registered. **`automation_safety(status)`** reports **`face_tool_opt_in`**. Docs: **`docs/SAFETY.md` §5** (wording tightened; no “creepware” framing).
- **README / help:** Marketing tone reduced; **`automation_system("help")`** returns structured docs (version, safety env, prompts, tool list). **`web_sota`** adds **`/help`** page; dashboard badges no longer show fake telemetry.

### Changed (tooling)
- **`automation_system`:** `Literal` aligned with implemented operations (`help` added; removed non-existent `screenshot` / `terminal` entries).

## [0.3.2] - 2026-03-21

### Changed
- **Discovery (Glama / PyPI):** `glama.json` and `pyproject.toml` package description lead with **safety** and **`virtualization-mcp`** for Sandbox/VM isolation; metadata aligned (version **0.3.2**, **FastMCP 3.1+**, `safety_and_isolation` feature block, keywords).
- **README:** Added **Discovery** subsection — stars reflect distribution, not safety; link to fleet isolation server.

## [0.3.1] - 2026-01-25

### Fixed
- **Docstring Refactoring**: Fixed missing blank lines after sections (D413) across all 8 portmanteau tools.
- **SOTA 2026 Alignment**: Standardized documentation to Jan 2026 industrial SOTA patterns.

### Added
- **Formal PRD**: Created `docs/PRD.md` to define project requirements and technical standards.
- **Improved Grounding**: Enhanced tool documentation for better AI agent navigation.

## [0.3.0] - 2025-10-08

### Added
- Comprehensive DXT manifest with 22+ automation tools
- Extensive prompt templates for conversational AI interaction
- GitHub Actions CI/CD pipeline with automated testing
- Issue and pull request templates for better contributions
- Contributing guidelines and development documentation

### Changed
- Reorganized repository structure with dedicated `dxt/` directory
- Updated pywin32 dependency to version 311
- Enhanced package metadata and descriptions

## [0.2.0] - 2025-01-23

### Added
- **Complete DXT Package**: Comprehensive Windows UI automation with face recognition
- **22 Automation Tools**: Window management, element interaction, OCR, mouse/keyboard control
- **Dual Interface Architecture**: MCP tools + REST API with feature parity
- **Face Recognition Security**: Webcam authentication and intruder detection
- **OCR Integration**: Text extraction from windows and images
- **Advanced Element Interaction**: Click, type, hover, and drag operations

### Changed
- Major architecture overhaul with modular plugin system
- Enhanced error handling and retry mechanisms
- Improved configuration management

## [0.1.0] - 2025-07-30

### Added
- Initial PyWinAuto MCP server implementation
- Basic window management tools
- Face recognition API endpoints
- Security monitoring features
- DXT packaging support

### Changed
- Initial release with core automation functionality

---

## 📊 Version Information

- **Current Version**: 0.2.0
- **Python Support**: 3.10, 3.11, 3.12
- **Platform**: Windows 10/11
- **License**: MIT

## 🔄 Release Process

Releases are automated through GitHub Actions:
1. Push to `master` branch triggers CI
2. Tests run on Windows with multiple Python versions
3. DXT package is built and uploaded as artifact
4. Release creation triggers final package distribution

## 🤝 Contributing to Changelog

When contributing to this project, please:
- Add entries to the "Unreleased" section above
- Use present tense for changes ("Add feature" not "Added feature")
- Group changes under appropriate headings (Added, Changed, Fixed, etc.)
- Reference issue numbers when applicable

---

*For more detailed information about each release, see the [GitHub Releases](https://github.com/yourusername/pywinauto-mcp/releases) page.*
