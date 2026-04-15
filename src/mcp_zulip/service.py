"""Zulip API client wrapper (singleton)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import zulip

from mcp_zulip.config import ZulipConfigError, ZulipSettings, load_settings, validate_settings

_client: zulip.Client | None = None


def _build_client(settings: ZulipSettings) -> zulip.Client:
    if settings.config_file:
        return zulip.Client(config_file=str(Path(settings.config_file).expanduser()))
    assert settings.email and settings.api_key and settings.site
    return zulip.Client(
        email=settings.email,
        api_key=settings.api_key,
        site=settings.site,
    )


def get_client() -> zulip.Client:
    """Return a shared Zulip client, creating it on first use."""
    global _client
    if _client is None:
        settings = load_settings()
        validate_settings(settings)
        try:
            _client = _build_client(settings)
        except zulip.ConfigNotFoundError as e:
            raise ZulipConfigError(str(e)) from e
    return _client


def reset_client_for_tests() -> None:
    """Clear singleton (tests only)."""
    global _client
    _client = None


def ensure_zulip_configured() -> None:
    """Validate configuration without creating the HTTP client."""
    s = load_settings()
    validate_settings(s)


class ZulipService:
    """Thin typed facade over zulip.Client for tools."""

    def __init__(self, client: zulip.Client) -> None:
        self._c = client

    @staticmethod
    def default() -> ZulipService:
        return ZulipService(get_client())

    def send_stream_message(self, stream: str, topic: str, content: str) -> dict[str, Any]:
        return self._c.send_message(
            {"type": "stream", "to": stream, "subject": topic, "content": content}
        )

    def send_private_message(self, user_emails: list[str], content: str) -> dict[str, Any]:
        return self._c.send_message(
            {"type": "private", "to": user_emails, "content": content},
        )

    def get_messages(
        self,
        narrow: list[dict[str, Any]],
        anchor: str = "newest",
        num_before: int = 50,
        num_after: int = 0,
    ) -> dict[str, Any]:
        num_before = max(1, min(int(num_before), 5000))
        num_after = max(0, min(int(num_after), 5000))
        return self._c.get_messages(
            {
                "anchor": anchor,
                "num_before": num_before,
                "num_after": num_after,
                "narrow": narrow,
            }
        )

    def get_unread_dm_messages(self, limit: int = 100) -> dict[str, Any]:
        lim = max(1, min(int(limit), 5000))
        return self._c.get_messages(
            {
                "anchor": "newest",
                "num_before": lim,
                "num_after": 0,
                "narrow": [
                    {"operator": "is", "operand": "unread"},
                    {"operator": "is", "operand": "dm"},
                ],
            }
        )

    def update_message(self, message_id: int, content: str) -> dict[str, Any]:
        return self._c.update_message({"message_id": message_id, "content": content})

    def delete_message(self, message_id: int) -> dict[str, Any]:
        return self._c.delete_message(message_id)

    def add_reaction(self, message_id: int, emoji_name: str) -> dict[str, Any]:
        return self._c.add_reaction({"message_id": message_id, "emoji_name": emoji_name})

    def remove_reaction(self, message_id: int, emoji_name: str) -> dict[str, Any]:
        return self._c.remove_reaction({"message_id": message_id, "emoji_name": emoji_name})

    def mark_all_as_read(self) -> dict[str, Any]:
        return self._c.mark_all_as_read()

    def mark_stream_as_read(self, stream_id: int) -> dict[str, Any]:
        return self._c.mark_stream_as_read(stream_id)

    def mark_topic_as_read(self, stream_id: int, topic_name: str) -> dict[str, Any]:
        return self._c.mark_topic_as_read(stream_id, topic_name)

    def get_raw_message(self, message_id: int) -> dict[str, Any]:
        return self._c.get_raw_message(message_id)

    def update_message_flags(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._c.update_message_flags(payload)

    def list_subscriptions(self) -> dict[str, Any]:
        return self._c.get_subscriptions()

    def subscribe_streams(
        self,
        streams: list[dict[str, Any]],
        invite_only: bool = False,
        principals: list[int] | list[str] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"streams": streams, "invite_only": invite_only}
        if principals is not None:
            kwargs["principals"] = principals
        return self._c.add_subscriptions(**kwargs)

    def get_stream_id(self, stream: str) -> dict[str, Any]:
        return self._c.get_stream_id(stream)

    def get_users(
        self,
        client_gravatar: bool | None = None,
        include_custom_profile_fields: bool = False,
    ) -> dict[str, Any]:
        req: dict[str, Any] = {}
        if client_gravatar is not None:
            req["client_gravatar"] = client_gravatar
        if include_custom_profile_fields:
            req["include_custom_profile_fields"] = include_custom_profile_fields
        return self._c.get_users(req or None)

    def get_members(self) -> dict[str, Any]:
        return self._c.get_members()

    def get_user_by_id(self, user_id: int) -> dict[str, Any]:
        return self._c.get_user_by_id(user_id)

    def format_user_mention_for_email(self, email: str) -> dict[str, Any]:
        """Resolve delivery_email to @**Full Name** mention syntax."""
        result = self.get_members()
        if result.get("result") != "success":
            return {
                "result": "error",
                "msg": result.get("msg", "get_members failed"),
                "mention": None,
            }
        members = result.get("members", [])
        for m in members:
            if m.get("delivery_email") == email or m.get("email") == email:
                name = m.get("full_name") or email
                return {"result": "success", "mention": f"@**{name}**", "user_id": m.get("user_id")}
        return {
            "result": "success",
            "mention": f"@**{email}**",
            "user_id": None,
            "note": "user not found; fallback email mention",
        }

    def call_endpoint(
        self,
        url: str,
        method: str = "POST",
        request: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._c.call_endpoint(url=url, method=method, request=request or {})
