"""Load packaged Markdown for MCP resources."""

from __future__ import annotations

import importlib.resources


def load_resource_markdown(filename: str) -> str:
    """Return UTF-8 text of a file under ``mcp_zulip.resources``."""
    root = importlib.resources.files("mcp_zulip.resources")
    return root.joinpath(filename).read_text(encoding="utf-8")
