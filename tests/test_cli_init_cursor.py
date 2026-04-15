import json
import subprocess
import sys
from pathlib import Path


def test_init_cursor_writes_mcp_json(tmp_path: Path) -> None:
    rc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_zulip",
            "init-cursor",
            "--directory",
            str(tmp_path),
            "--server-name",
            "zulip",
            "--use-env",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert rc.returncode == 0, rc.stderr
    out = tmp_path / ".cursor" / "mcp.json"
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "mcpServers" in data
    assert "zulip" in data["mcpServers"]
    assert data["mcpServers"]["zulip"]["args"] == ["-m", "mcp_zulip"]
    assert "${env:ZULIP_EMAIL}" in data["mcpServers"]["zulip"]["env"]["ZULIP_EMAIL"]


def test_init_cursor_rejects_invalid_json(tmp_path: Path) -> None:
    cursor = tmp_path / ".cursor"
    cursor.mkdir(parents=True)
    (cursor / "mcp.json").write_text("{ not json", encoding="utf-8")
    rc = subprocess.run(
        [sys.executable, "-m", "mcp_zulip", "init-cursor", "--directory", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert rc.returncode == 1
    assert "invalid JSON" in rc.stderr.lower() or "invalid" in rc.stderr.lower()


def test_init_cursor_merges_existing_servers(tmp_path: Path) -> None:
    cursor = tmp_path / ".cursor"
    cursor.mkdir(parents=True)
    existing = {"mcpServers": {"other": {"command": "true", "args": []}}}
    (cursor / "mcp.json").write_text(json.dumps(existing), encoding="utf-8")
    subprocess.run(
        [sys.executable, "-m", "mcp_zulip", "init-cursor", "--directory", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads((cursor / "mcp.json").read_text(encoding="utf-8"))
    assert "other" in data["mcpServers"]
    assert "zulip" in data["mcpServers"]
