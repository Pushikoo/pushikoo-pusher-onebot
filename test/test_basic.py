import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from pushikoo_interface import get_adapter_test_env, run_pusher_basic_flow

from pushikoo_pusher_onebot.config import AdapterConfig, Bot, Contact, InstanceConfig


def test_basic_flow():
    load_dotenv()
    bot_url = os.getenv("BOT_URL")
    target_id = os.getenv("TARGET_ID")
    if not bot_url or not target_id:
        pytest.skip("BOT_URL and TARGET_ID are required for the integration test")

    adapter_config = AdapterConfig(
        bots={
            "bot0": Bot(
                token=os.getenv("BOT_TOKEN"),
                url=bot_url,
            )
        }
    )
    instance_config = InstanceConfig(
        bot="bot0",
        contact=Contact(id=target_id, private=os.getenv("TARGET_PRIVATE") == "true"),
    )
    pusher, ctx = get_adapter_test_env(
        Path(__file__).parents[1] / "pyproject.toml",
        adapter_config=adapter_config,
        adapter_instance_config=instance_config,
    )
    run_pusher_basic_flow(pusher, ctx)


if __name__ == "__main__":
    test_basic_flow()
