import json
import os

from .bark import Bark
from .pushplus import Pushplus
from .qmsg import Qmsg
from .server import Server
from .wechat import WorkWechatApp, WorkWechatRobot
from .mail import Mail


class PushComposite:
    def __init__(self) -> None:
        self.children = {}

    def add(self, key: str, push) -> None:
        self.children[key] = push

    def send(self, msg: str, **kwargs) -> None:
        for push in self.children.values():
            push.send(msg, **kwargs)

    def remove(self, key: str) -> None:
        self.children.pop(key)


class PushSender:
    def __init__(self, type: str, key) -> None:
        self.push = self.create(type, key)

    def create(self, type: str, key):
        if type == "pushplus":
            return Pushplus(key)
        elif type in ("server", "serverChan", "serverchan"):
            return Server(key)
        elif type == "qmsg":
            return Qmsg(key)
        elif type == "workWechatRobot":
            return WorkWechatRobot(key)
        elif type == "workWechat":
            return WorkWechatApp(key)
        elif type == "bark":
            return Bark(key)
        elif type == "mail":
            # key转成json对象
            email_config = json.loads(key)
            return Mail(email_config['host'], email_config['user'], email_config['pass'], email_config['port'], email_config['from'], email_config['to'], email_config['receives'])

    def send(self, msg: str, **kwargs):
        print(f"推送消息：{msg}")
        self.push.send(msg, **kwargs)


def push_channels_from_env():
    """从环境变量构建推送渠道列表。

    优先读取 PUSH（JSON，支持单个 {type,key} 或 [{type,key}, ...]），
    再追加 SERVERCHAN_SENDKEY / BARK_URL 单独配置的渠道。
    """
    channels = []

    push_raw = os.environ.get("PUSH", "").strip()
    if push_raw:
        try:
            push_config = json.loads(push_raw, strict=False)
        except json.JSONDecodeError:
            push_config = None
        if isinstance(push_config, list):
            channels.extend(
                item for item in push_config
                if isinstance(item, dict) and item.get("type") and item.get("key")
            )
        elif isinstance(push_config, dict) and push_config.get("type") and push_config.get("key"):
            channels.append(push_config)

    serverchan_key = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
    if serverchan_key:
        channels.append({"type": "serverChan", "key": serverchan_key})

    bark_url = os.environ.get("BARK_URL", "").strip()
    if bark_url:
        channels.append({"type": "bark", "key": bark_url})

    return channels
