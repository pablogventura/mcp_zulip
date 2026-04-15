"""Shared helpers."""

from __future__ import annotations

import re


def strip_html(html: str | None) -> str:
    """Strip simple HTML tags and common entities from Zulip message content."""
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", "", html)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    return text.strip()
