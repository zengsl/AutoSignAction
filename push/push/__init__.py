from .pushplus import Pushplus
from .qmsg import Qmsg
from .server import Server
from .wechat import WorkWechatApp, WorkWechatRobot
from .mail import Mail
import json


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
        elif type == "server":
            return Server(key)
        elif type == "qmsg":
            return Qmsg(key)
        elif type == "workWechatRobot":
            return WorkWechatRobot(key)
        elif type == "workWechat":
            return WorkWechatApp(key)
        elif type == "email":
            # key转成json对象
            email_config = json.loads(key)
            return Mail(email_config['host'], email_config['user'], email_config['pass'], email_config['port'])

    def send(self, msg: str, **kwargs):
        print(f"推送消息：{msg}")
        self.push.send(msg, **kwargs)
