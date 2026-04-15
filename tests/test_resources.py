from mcp_zulip.resource_text import load_resource_markdown


def test_api_guide_contains_links_and_table() -> None:
    text = load_resource_markdown("api_guide.md")
    assert "https://zulip.com/api/rest" in text
    assert "| GET | `messages`" in text or "GET" in text and "messages" in text


def test_cheatsheet_mentions_api_guide_uri() -> None:
    text = load_resource_markdown("cheatsheet.md")
    assert "zulip://api-guide" in text
