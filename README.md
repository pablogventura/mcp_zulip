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

```bash
pipx install "mcp-zulip"
# or from a clone:
pipx install .
```

Develop with a virtualenv:

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Configure Cursor

### Quick merge (recommended)

From your project root (where `.cursor` should live):

```bash
mcp-zulip init-cursor
```

This creates or updates `.cursor/mcp.json` with:

- `"command":` the current Python interpreter  
- `"args": ["-m", "mcp_zulip"]`  
- `"env": { "ZULIP_CONFIG_FILE": "${workspaceFolder}/.zuliprc" }`  

Place your API file at `<project>/.zuliprc` (do **not** commit it).

Use API keys via environment placeholders instead:

```bash
mcp-zulip init-cursor --use-env
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
