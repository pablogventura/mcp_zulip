"""Register FastMCP tools and resources."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_zulip.resource_text import load_resource_markdown
from mcp_zulip.service import ZulipService
from mcp_zulip.util import strip_html


def register_resources(mcp: FastMCP) -> None:
    @mcp.resource(
        "zulip://api-guide",
        mime_type="text/markdown",
        name="zulip-api-guide",
        title="Zulip REST API guide for MCP",
        description=(
            "Official doc links and call_endpoint path cheat sheet. "
            "Read before zulip_call_endpoint."
        ),
    )
    def api_guide() -> str:
        return load_resource_markdown("api_guide.md")

    @mcp.resource(
        "zulip://call-endpoint-cheatsheet",
        mime_type="text/markdown",
        name="zulip-call-endpoint-cheatsheet",
        title="Zulip call_endpoint URL quick table",
        description="Short method/url table. Full narrative: zulip://api-guide.",
    )
    def cheatsheet() -> str:
        return load_resource_markdown("cheatsheet.md")


def register_tools(mcp: FastMCP) -> None:
    svc = ZulipService.default

    @mcp.tool()
    def send_stream_message(stream: str, topic: str, content: str) -> dict[str, Any]:
        """Send a message to a Zulip stream. Topic is the thread name."""
        return svc().send_stream_message(stream, topic, content)

    @mcp.tool()
    def send_private_message(user_emails: list[str], content: str) -> dict[str, Any]:
        """Send a direct (private) message. user_emails is one or more Zulip account emails."""
        return svc().send_private_message(user_emails, content)

    @mcp.tool()
    def get_messages(
        narrow: list[dict[str, Any]],
        anchor: str = "newest",
        num_before: int = 50,
        num_after: int = 0,
    ) -> dict[str, Any]:
        """Fetch messages with a Zulip narrow (list of {operator, operand}).

        Default num_before is modest; raise up to 5000 if needed.
        See zulip://api-guide and https://zulip.com/api/construct-narrow
        """
        return svc().get_messages(narrow, anchor=anchor, num_before=num_before, num_after=num_after)

    @mcp.tool()
    def get_unread_dm_messages(limit: int = 100) -> dict[str, Any]:
        """List recent unread direct messages for the current user (newest anchor)."""
        return svc().get_unread_dm_messages(limit)

    @mcp.tool()
    def update_message(message_id: int, content: str) -> dict[str, Any]:
        """Edit message body for a message ID you are allowed to edit."""
        return svc().update_message(message_id, content)

    @mcp.tool()
    def delete_message(message_id: int) -> dict[str, Any]:
        """Delete a message by ID (permission checks apply on the server)."""
        return svc().delete_message(message_id)

    @mcp.tool()
    def get_raw_message(message_id: int) -> dict[str, Any]:
        """Fetch one message (raw API shape: metadata and content fields)."""
        return svc().get_raw_message(message_id)

    @mcp.tool()
    def add_reaction(message_id: int, emoji_name: str) -> dict[str, Any]:
        """Add a unicode emoji reaction to a message (emoji_name e.g. +1, tada)."""
        return svc().add_reaction(message_id, emoji_name)

    @mcp.tool()
    def remove_reaction(message_id: int, emoji_name: str) -> dict[str, Any]:
        """Remove an emoji reaction from a message."""
        return svc().remove_reaction(message_id, emoji_name)

    @mcp.tool()
    def mark_all_as_read() -> dict[str, Any]:
        """Mark all messages as read for the current user."""
        return svc().mark_all_as_read()

    @mcp.tool()
    def mark_stream_as_read(stream_id: int) -> dict[str, Any]:
        """Mark all messages in a stream as read. Resolve stream name via get_stream_id."""
        return svc().mark_stream_as_read(stream_id)

    @mcp.tool()
    def mark_topic_as_read(stream_id: int, topic_name: str) -> dict[str, Any]:
        """Mark all messages in a topic within a stream as read."""
        return svc().mark_topic_as_read(stream_id, topic_name)

    @mcp.tool()
    def update_message_flags(
        messages: list[int],
        flag: str,
        op: str,
    ) -> dict[str, Any]:
        """Update personal flags (read, starred, …). Uses Zulip messages/flags fields."""
        return svc().update_message_flags({"messages": messages, "flag": flag, "op": op})

    @mcp.tool()
    def list_subscriptions() -> dict[str, Any]:
        """List streams (channels) the current user is subscribed to."""
        return svc().list_subscriptions()

    @mcp.tool()
    def subscribe_streams(
        stream_names: list[str],
        invite_only: bool = False,
    ) -> dict[str, Any]:
        """Subscribe to streams by name (server may create streams if allowed)."""
        streams = [{"name": n} for n in stream_names]
        return svc().subscribe_streams(streams, invite_only=invite_only)

    @mcp.tool()
    def get_stream_id(stream: str) -> dict[str, Any]:
        """Resolve a stream name to stream_id for APIs that require stream_id."""
        return svc().get_stream_id(stream)

    @mcp.tool()
    def get_users(include_custom_profile_fields: bool = False) -> dict[str, Any]:
        """List realm users. Large on big orgs; filter via zulip_call_endpoint if needed."""
        return svc().get_users(include_custom_profile_fields=include_custom_profile_fields)

    @mcp.tool()
    def format_user_mention_for_email(email: str) -> dict[str, Any]:
        """Return @**Full Name** mention syntax for an email if the user exists."""
        return svc().format_user_mention_for_email(email)

    @mcp.tool()
    def strip_html_content(html: str) -> dict[str, Any]:
        """Strip simple HTML from Zulip message content to plain text (helper for summarization)."""
        return {"result": "success", "text": strip_html(html)}

    @mcp.tool()
    def zulip_call_endpoint(
        url: str,
        method: str = "POST",
        request: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generic Zulip REST call via Python call_endpoint.

        `url` is the relative API path (e.g. messages), not the full site URL.
        Read zulip://api-guide first. Destructive/admin actions are possible.
        """
        return svc().call_endpoint(url=url, method=method.upper(), request=request)
