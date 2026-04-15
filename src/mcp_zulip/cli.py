"""Console entry: stdio MCP server or init-cursor helper."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp_zulip.config import ZulipConfigError
from mcp_zulip.server import run_stdio_server
from mcp_zulip.service import ensure_zulip_configured


def _merge_mcp_servers(
    existing: Any,
    server_name: str,
    entry: dict[str, Any],
) -> dict[str, Any]:
    if existing is None:
        return {server_name: entry}
    if not isinstance(existing, dict):
        raise ValueError("Existing mcpServers must be a JSON object")
    merged = dict(existing)
    merged[server_name] = entry
    return merged


def resolve_cursor_project_root(start: Path, *, use_cwd_only: bool) -> Path:
    """Directory where Cursor expects project `.cursor/mcp.json`: repo root, not a subfolder.

    Uses ``git rev-parse --show-toplevel`` from ``start``, then walking parents for ``.git``.
    If ``use_cwd_only`` is True, returns ``start.resolve()`` without git detection.
    """
    start = start.resolve()
    if use_cwd_only:
        return start
    try:
        cp = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if cp.returncode == 0 and (out := cp.stdout.strip()):
            return Path(out).resolve()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p.resolve()
    return start


def cmd_init_cursor(args: argparse.Namespace) -> int:
    """Write or merge ``<project>/.cursor/mcp.json`` (Cursor project MCP path)."""
    start = Path(args.directory).resolve()
    root = resolve_cursor_project_root(start, use_cwd_only=args.use_cwd)
    cursor_dir = root / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    target = cursor_dir / "mcp.json"

    cfg: dict[str, Any] = {}
    if target.is_file():
        raw = target.read_text(encoding="utf-8")
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"mcp-zulip: invalid JSON in {target}: {e}", file=sys.stderr)
            return 1
        if not isinstance(loaded, dict):
            print("mcp-zulip: root of mcp.json must be a JSON object", file=sys.stderr)
            return 1
        cfg = loaded

    if args.use_env:
        env_block = {
            "ZULIP_EMAIL": "${env:ZULIP_EMAIL}",
            "ZULIP_API_KEY": "${env:ZULIP_API_KEY}",
            "ZULIP_SITE": "${env:ZULIP_SITE}",
        }
    else:
        env_block = {
            "ZULIP_CONFIG_FILE": "${workspaceFolder}/.zuliprc",
        }

    entry = {
        "command": args.python_executable,
        "args": ["-m", "mcp_zulip"],
        "env": env_block,
    }

    try:
        cfg["mcpServers"] = _merge_mcp_servers(cfg.get("mcpServers"), args.server_name, entry)
    except ValueError as e:
        print(f"mcp-zulip: {e}", file=sys.stderr)
        return 1

    target.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    rel = f" (from cwd {start})" if root != start else ""
    print(f"mcp-zulip: wrote {target} (server key: {args.server_name!r}){rel}")
    return 0


def main() -> None:
    argv = list(sys.argv[1:])
    # Users often try `--init-cursor` (flag style); that must not start the MCP server
    # or require Zulip credentials — only the `init-cursor` subcommand does.
    if argv and argv[0] in ("--init-cursor", "-init-cursor"):
        argv[0] = "init-cursor"

    if argv and argv[0] == "init-cursor":
        parser = argparse.ArgumentParser(prog="mcp-zulip init-cursor")
        parser.add_argument(
            "--directory",
            "-C",
            default=".",
            help=(
                "Starting directory (default: .). Resolves git root for .cursor/mcp.json "
                "unless --use-cwd."
            ),
        )
        parser.add_argument(
            "--use-cwd",
            action="store_true",
            help="Write .cursor/mcp.json under -C only (no git root). For non-git projects.",
        )
        parser.add_argument(
            "--server-name",
            default="zulip",
            help="Key under mcpServers (default: zulip)",
        )
        parser.add_argument(
            "--python-executable",
            default=sys.executable,
            help="Python to invoke for -m mcp_zulip (default: current interpreter)",
        )
        parser.add_argument(
            "--use-env",
            action="store_true",
            help=(
                "Use ZULIP_EMAIL, ZULIP_API_KEY, ZULIP_SITE placeholders "
                "instead of ZULIP_CONFIG_FILE"
            ),
        )
        ns = parser.parse_args(argv[1:])
        raise SystemExit(cmd_init_cursor(ns))

    try:
        ensure_zulip_configured()
    except ZulipConfigError as e:
        print(f"mcp-zulip: {e}", file=sys.stderr)
        raise SystemExit(1) from e

    run_stdio_server()


if __name__ == "__main__":
    main()
