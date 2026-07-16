# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup (uses uv, not pip/venv directly)
uv venv
source .venv/bin/activate
uv pip install -e .

# Run the MCP server
uv run main.py

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_docx
```

## Architecture

This is an MCP (Model Context Protocol) server exposing tools for AI assistants, built with `mcp[cli]` (FastMCP).

- `main.py` — server entrypoint. Creates the `FastMCP("docs")` instance and registers tools via `mcp.tool()(function)`. **Only tools explicitly registered here are exposed** — e.g. `tools/document.py` currently defines `binary_document_to_markdown` but it is not registered in `main.py`, so it exists only as a plain importable function/is only covered by tests, not exposed via MCP yet.
- `tools/` — plain Python functions implementing tool logic, one concern per module (`math.py`, `document.py`). These are framework-agnostic; MCP registration happens only in `main.py`.
- `tools/document.py` — converts binary document data (docx, pdf, etc.) to markdown using `markitdown`, via an in-memory `BytesIO` stream and `StreamInfo` for format detection.
- `tests/` — pytest tests import directly from `tools.*`, not through the MCP layer. Fixtures for document conversion tests live in `tests/fixtures/` (sample `.docx`/`.pdf` files).

### Adding a new tool

Tools are plain Python functions; MCP-specific wiring is just the `mcp.tool()(fn)` registration call in `main.py`.

1. Implement the function in `tools/<module>.py`:
   - Annotate each parameter with `pydantic.Field(description=...)` describing what that parameter does (see `add` in `tools/math.py`).
   - Write the docstring — this is what the AI assistant sees as the tool description, so treat it as the primary interface contract:
     - One-line summary first
     - Detailed explanation of functionality
     - "When to use" (and when not to use) section
     - Usage examples with expected input/output, doctest-style (`>>> add(2, 3)` / `5.0`)
   - `tools/document.py`'s `binary_document_to_markdown` currently has only a one-line docstring and no `Field` annotations — it does not yet follow this convention and is a useful example of what to fix when touching that file.
2. Register it in `main.py` with `mcp.tool()(my_function)`. A function not registered here is not exposed to the MCP client, even if fully implemented and tested.
3. Add tests under `tests/` that import the function directly from `tools.*` (tests bypass the MCP layer entirely).
