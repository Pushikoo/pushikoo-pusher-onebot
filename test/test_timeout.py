import base64
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from pushikoo_pusher_onebot.api import OneBotAPIClient, image_to_base64
from pushikoo_pusher_onebot.config import Bot


def test_message_request_uses_configured_timeout():
    response = Mock()
    response.json.return_value = {"status": "ok"}
    client = OneBotAPIClient("http://onebot.local", timeout_seconds=42)

    with patch(
        "pushikoo_pusher_onebot.api.requests.post", return_value=response
    ) as post:
        client.send_private_msg(123, [{"type": "text", "data": {"text": "hi"}}])

    post.assert_called_once()
    assert post.call_args.kwargs["timeout"] == (10, 42)
    response.raise_for_status.assert_called_once_with()


def test_remote_image_request_uses_configured_timeout():
    response = Mock(content=b"image")

    with patch("pushikoo_pusher_onebot.api.requests.get", return_value=response) as get:
        encoded = image_to_base64("https://example.com/image.png", 17)

    assert encoded == base64.b64encode(b"image").decode()
    get.assert_called_once_with("https://example.com/image.png", timeout=(10, 17))
    response.raise_for_status.assert_called_once_with()


def test_request_timeout_must_be_positive():
    with pytest.raises(ValidationError):
        Bot(url="http://onebot.local", request_timeout_seconds=0)
