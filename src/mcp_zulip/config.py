"""Load Zulip credentials from environment or zuliprc path."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ZulipConfigError(RuntimeError):
    """Missing or invalid configuration for Zulip."""


@dataclass(frozen=True)
class ZulipSettings:
    """Either `config_file` is set, or all of email, api_key, site."""

    config_file: str | None
    email: str | None
    api_key: str | None
    site: str | None


def load_settings() -> ZulipSettings:
    """Read settings from environment variables."""
    cf = os.environ.get("ZULIP_CONFIG_FILE") or os.environ.get("ZULIPRC")
    email = os.environ.get("ZULIP_EMAIL")
    api_key = os.environ.get("ZULIP_API_KEY")
    site = os.environ.get("ZULIP_SITE")
    if cf:
        return ZulipSettings(config_file=cf.strip(), email=None, api_key=None, site=None)
    return ZulipSettings(config_file=None, email=email, api_key=api_key, site=site)


def validate_settings(settings: ZulipSettings) -> None:
    """Ensure credentials are present on disk or in env (no network check)."""
    if settings.config_file:
        path = Path(settings.config_file).expanduser()
        if not path.is_file():
            raise ZulipConfigError(
                f"ZULIP_CONFIG_FILE points to a missing file: {path}. "
                "Download a zuliprc from your Zulip account settings."
            )
        return
    missing = [
        name
        for name, val in (
            ("ZULIP_EMAIL", settings.email),
            ("ZULIP_API_KEY", settings.api_key),
            ("ZULIP_SITE", settings.site),
        )
        if not val
    ]
    if missing:
        raise ZulipConfigError(
            "Set either ZULIP_CONFIG_FILE (path to zuliprc) or all of: "
            f"ZULIP_EMAIL, ZULIP_API_KEY, ZULIP_SITE. Missing: {', '.join(missing)}"
        )
