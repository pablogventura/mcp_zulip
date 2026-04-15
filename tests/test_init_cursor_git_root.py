import json
import subprocess
import sys
from pathlib import Path


def test_init_cursor_uses_git_toplevel_not_subdir(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    sub = tmp_path / "src" / "nested"
    sub.mkdir(parents=True)
    rc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_zulip",
            "init-cursor",
            "--directory",
            str(sub),
            "--use-env",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert rc.returncode == 0, rc.stderr
    root_mcp = tmp_path / ".cursor" / "mcp.json"
    assert root_mcp.is_file(), "expected project-level path at git root"
    data = json.loads(root_mcp.read_text(encoding="utf-8"))
    assert "zulip" in data["mcpServers"]
    assert not (sub / ".cursor" / "mcp.json").exists()


def test_init_cursor_use_cwd_writes_under_given_dir(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    sub = tmp_path / "nested"
    sub.mkdir()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_zulip",
            "init-cursor",
            "--directory",
            str(sub),
            "--use-cwd",
            "--use-env",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert (sub / ".cursor" / "mcp.json").is_file()
