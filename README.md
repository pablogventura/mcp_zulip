# mcp-zulip

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for [Zulip](https://zulip.com/). It exposes curated tools for common chat operations plus `zulip_call_endpoint` for the full REST API surface supported by the official Python client.

**Read-only MCP resources** (fetch before using `zulip_call_endpoint`):

- `zulip://api-guide` — official doc links and `call_endpoint` path cheat sheet  
- `zulip://call-endpoint-cheatsheet` — short method/url table  

## Requirements

- Python 3.10+
- Zulip credentials: either a downloaded **`zuliprc`** file, or **`ZULIP_EMAIL`**, **`ZULIP_API_KEY`**, and **`ZULIP_SITE`** (your organization URL, e.g. `https://chat.zulip.org`).

Use a **dedicated bot account** with minimal permissions when the MCP is shared or automated.

## Install

### From PyPI (when published)

```bash
pipx install mcp-zulip
```

### From a local checkout

Inside the repo (or pass an absolute path to the project root):

```bash
cd /path/to/mcp_zulip
pipx install .
# same idea:
pipx install /path/to/mcp_zulip
```

### From GitHub (no local clone)

Install the latest `main` straight from the remote:

```bash
pipx install "git+https://github.com/pablogventura/mcp_zulip.git"
```

To pin a branch or tag:

```bash
pipx install "git+https://github.com/pablogventura/mcp_zulip.git@v0.1.0"
pipx install "git+https://github.com/pablogventura/mcp_zulip.git@main"
```

(`pip` also accepts `git+https://…`; `pipx` delegates to pip under the hood.)

Develop with a virtualenv:

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Configure Cursor

### Quick merge (recommended)

Cursor loads **project** MCP config from **`<workspaceFolder>/.cursor/mcp.json`** (the folder you open in Cursor), not from arbitrary subdirectories. User-level config is separate: `~/.cursor/mcp.json` (not modified by `init-cursor`).

`init-cursor` writes exactly there: it resolves the **Git repository root** from your current directory (same idea as opening the repo in Cursor). So you can run it from a subfolder and it still updates the root:

```bash
cd /path/to/my-repo
mcp-zulip init-cursor
# equivalent (no Zulip env needed for this step):
mcp-zulip --init-cursor
# or from my-repo/src/pkg:
cd /path/to/my-repo/src/pkg
mcp-zulip init-cursor   # still writes /path/to/my-repo/.cursor/mcp.json
```

If you are **not** using Git, or you really want the file under the current directory only:

```bash
mcp-zulip init-cursor --use-cwd
```

This creates or updates `.cursor/mcp.json` with:

- `"command":` the current Python interpreter  
- `"args": ["-m", "mcp_zulip"]`  
- `"env": { "ZULIP_CONFIG_FILE": "${workspaceFolder}/.zuliprc" }`  

Place your API file at `<project>/.zuliprc` (do **not** commit it).

Use API keys via environment placeholders instead:

```bash
mcp-zulip init-cursor --use-env
# or:
mcp-zulip --init-cursor --use-env
```

If Cursor’s GUI does not inherit your shell `PATH`, set `"command"` to an **absolute** path to the Python binary (or to the `mcp-zulip` script from `pipx`).

### Manual snippet

See [`.cursor/mcp.json.example`](.cursor/mcp.json.example). Cursor interpolates `${env:VAR}` and `${workspaceFolder}`; see [Cursor MCP docs](https://cursor.com/docs/mcp).

## Run (stdio)

Cursor runs this automatically when MCP is enabled. Manually:

```bash
export ZULIP_CONFIG_FILE="$HOME/.zuliprc"
python -m mcp_zulip
```

## Security

- **Never** commit `.zuliprc` or API keys. Add `.zuliprc` to `.gitignore`.
- Rotate any key that was ever committed, pushed to a remote, or pasted into a chat log.
- `zulip_call_endpoint` can perform **destructive or administrative** actions allowed by the account. Prefer narrow bot permissions.

## Tools (summary)

| Tool | Purpose |
|------|---------|
| `send_stream_message` | Post to a stream (channel) |
| `send_private_message` | DM one or more users by email |
| `get_messages` | Fetch with a Zulip narrow |
| `get_unread_dm_messages` | Unread DMs |
| `update_message` / `delete_message` | Edit / delete |
| `get_raw_message` | Single message payload |
| `add_reaction` / `remove_reaction` | Emoji reactions |
| `mark_all_as_read` / `mark_stream_as_read` / `mark_topic_as_read` | Read receipts |
| `update_message_flags` | Star/read flags API |
| `list_subscriptions` | Subscribed streams |
| `subscribe_streams` | Subscribe by name |
| `get_stream_id` | Resolve stream name → id |
| `get_users` | List realm users |
| `format_user_mention_for_email` | Build `@**Name**` |
| `strip_html_content` | Plain text from HTML body |
| `zulip_call_endpoint` | Escape hatch to any REST path |

## Limitations

- **Real-time event queues** (`register` / long-poll `events`) are not exposed as MCP tools (blocking, long-lived). Use REST, bots, or a separate worker if you need streaming.

## License

MIT — see [LICENSE](LICENSE).
