import base64
from unittest.mock import Mock, patch

import pytest
from pushikoo_interface import ImageBlob, Struct, StructImage
from pushikoo_pusher_onebot.api import OneBotAPIClient
from pushikoo_pusher_onebot.config import (
    AdapterConfig,
    Bot,
    Contact,
    ImageSendMethod,
    InstanceConfig,
)
from pushikoo_pusher_onebot.main import OneBot
from pydantic import ValidationError


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
    ctx = Mock()
    ctx.get_config.return_value = AdapterConfig(
        bots={"bot0": Bot(url="http://onebot.local", request_timeout_seconds=17)}
    )
    ctx.get_instance_config.return_value = InstanceConfig(
        bot="bot0",
        contact=Contact(id="123"),
        image_send_method=ImageSendMethod.BASE64,
    )
    ctx.get_proxies.return_value = None
    ctx.read_image.return_value = ImageBlob(
        data=b"image",
        content_type="image/png",
        filename="image.png",
    )
    pusher = OneBot.__new__(OneBot)
    pusher.ctx = ctx

    with patch.object(OneBotAPIClient, "send_group_msg") as send:
        pusher.push(
            Struct(content=[StructImage(source="https://example.com/image.png")])
        )

    ctx.read_image.assert_called_once_with("https://example.com/image.png", timeout=17)
    send.assert_called_once_with(
        123,
        [
            {
                "type": "image",
                "data": {"file": "base64://" + base64.b64encode(b"image").decode()},
            }
        ],
    )


def test_request_timeout_must_be_positive():
    with pytest.raises(ValidationError):
        Bot(url="http://onebot.local", request_timeout_seconds=0)
