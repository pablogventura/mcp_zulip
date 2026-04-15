from unittest.mock import MagicMock

import pytest

from mcp_zulip import service as service_mod
from mcp_zulip.service import ZulipService


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    service_mod.reset_client_for_tests()
    yield
    service_mod.reset_client_for_tests()


def test_send_stream_message_delegates() -> None:
    client = MagicMock()
    client.send_message.return_value = {"result": "success"}
    s = ZulipService(client)
    out = s.send_stream_message("general", "topic", "hi")
    assert out["result"] == "success"
    client.send_message.assert_called_once_with(
        {"type": "stream", "to": "general", "subject": "topic", "content": "hi"}
    )


def test_call_endpoint_passes_through() -> None:
    client = MagicMock()
    client.call_endpoint.return_value = {"result": "success"}
    s = ZulipService(client)
    s.call_endpoint("users", "GET", {"client_gravatar": True})
    client.call_endpoint.assert_called_once_with(
        url="users", method="GET", request={"client_gravatar": True}
    )
