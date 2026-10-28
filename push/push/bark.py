from urllib.parse import urlencode

import requests as re

from .decorator import catchException
from .push import Push


class Bark(Push):
    """
    Bark 推送
    官方文档: https://github.com/Finb/Bark
    key 可填设备 key，也可填完整推送地址(如 https://api.day.app/<key> 或自建服务地址)
    """

    default_url = "https://api.day.app"

    # Bark 可选参数
    optional_params = ("sound", "group", "level", "url", "icon", "badge", "copy")

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.url = self.build_url(key)

    @staticmethod
    def build_url(key: str) -> str:
        key = key.strip()
        if key.startswith(("http://", "https://")):
            return key.rstrip("/")
        return f"{Bark.default_url}/{key}"

    @catchException
    def send(self, msg: str, **kwargs) -> None:
        body = str(msg)
        # Bark 单条消息有长度上限，超长时截断保底
        if len(body) > 3800:
            body = body[:3800] + "\n…（内容过长已截断）"

        data = {
            "title": kwargs.get("title", "No title"),
            "body": body,
        }

        params = {key: kwargs[key] for key in self.optional_params if kwargs.get(key)}
        target = f"{self.url}?{urlencode(params)}" if params else self.url

        res = re.post(target, json=data, timeout=15)

        try:
            result = res.json()
        except ValueError:
            if res.status_code == 200:
                self.success()
                return
            raise Exception(f"HTTP {res.status_code}: {res.text[:200]}")

        if result.get("code") == 200:
            self.success()
        else:
            raise Exception(result.get("message") or str(result.get("code")))
