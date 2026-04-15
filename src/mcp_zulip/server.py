"""FastMCP server factory and stdio entry."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_zulip.register_tools import register_resources, register_tools


def build_mcp() -> FastMCP:
    mcp = FastMCP(
        "mcp-zulip",
        instructions=(
            "Zulip workspace integration. Before calling zulip_call_endpoint, read the resource "
            "zulip://api-guide (or zulip://call-endpoint-cheatsheet) for correct REST paths."
        ),
    )
    register_resources(mcp)
    register_tools(mcp)
    return mcp


def run_stdio_server() -> None:
    """Run the MCP server over stdio (used by Cursor)."""
    mcp = build_mcp()
    mcp.run(transport="stdio")
