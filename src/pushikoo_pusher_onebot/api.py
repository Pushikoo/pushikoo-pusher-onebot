import base64
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests


def image_to_base64(source: str, timeout_seconds: float = 60) -> str:
    """Convert image URL or local path to base64 string."""
    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=(10, timeout_seconds))
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    elif source.startswith("file://"):
        parsed = urlparse(source)
        path = Path(unquote(parsed.path.lstrip("/")))
        return base64.b64encode(path.read_bytes()).decode()


class OneBotAPIClient:
    def __init__(
        self,
        url: str,
        token: str | None = None,
        proxies: dict | None = None,
        timeout_seconds: float = 60,
    ):
        self.url = url.rstrip("/")
        self.token = token
        self.proxies = proxies
        self.timeout = (10, timeout_seconds)

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def send_private_msg(self, user_id: int, message: list[dict]) -> dict:
        response = requests.post(
            f"{self.url}/send_private_msg",
            json={"user_id": user_id, "message": message},
            headers=self._headers(),
            proxies=self.proxies,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "failed":
            raise Exception(data.get("message", data))
        return data

    def send_group_msg(self, group_id: int, message: list[dict]) -> dict:
        response = requests.post(
            f"{self.url}/send_group_msg",
            json={"group_id": group_id, "message": message},
            headers=self._headers(),
            proxies=self.proxies,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "failed":
            raise Exception(data.get("message", data))
        return data
