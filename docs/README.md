# Documentation index

**Package docs hub** (align with root **README** and **[CHANGELOG.md](../CHANGELOG.md)** for release notes — e.g. **v0.4.2** pointer backend, optional **global keylogger**, examples **`just demo`**).

| Document | Description |
|----------|-------------|
| [**PRD.md**](PRD.md) | Product requirements — tools, web_sota, REST/LLM/cameras, testing strategy |
| [**SAFETY.md**](SAFETY.md) | Isolation, HITL (human-in-the-loop), face opt-in, dual-use / keylogger, two-server model |
| [**OPERATOR_PROTOCOL.md**](OPERATOR_PROTOCOL.md) | Foreground / focus during automation |
| [**TESTING.md**](TESTING.md) | CI vs local pytest, markers, commands |
| [**LLM_REPO_CONTEXT.md**](LLM_REPO_CONTEXT.md) | Pointer to canonical chat system prompt source (`llm_repo_context.py`) |

Fleet cross-references: **mcp-central-docs** — `patterns/PYWINAUTO_MCP_SAFETY.md`, `standards/testing-environment-aware.md`. **Sibling automation server:** **[autohotkey-mcp](https://github.com/sandraschi/autohotkey-mcp)** (AutoHotkey scriptlets — overlap and differences in root **README**, *Complementary: autohotkey-mcp*).

**Scope:** This project is **desktop / native UI automation** (see root **README** — *Native Windows vs websites*). **Website** work belongs on a **browser MCP** (commonly **Playwright**); the stacks are orthogonal.
