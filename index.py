import json
import sys , os
import time
from push.tools.tools import failed, handler, info, success


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from bilibili import BiliBili
from push import PushSender, parse
from email_notifier import send_bilibili_notification

import logging
from logging import handlers

log = None




def build_logger(base_name):
    """日志构建"""
    log = logging.getLogger(base_name)
    log.setLevel(logging.DEBUG)
    if log.handlers:
        return log
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log_handler.setLevel(level=logging.INFO)
    log_handler.setFormatter(formatter)
    if not os.path.exists(f'{base_name}'):
        os.makedirs(f'{base_name}')
    time_rotating_file_handler = handlers.TimedRotatingFileHandler(f'{base_name}/log.log', when='D')
    time_rotating_file_handler.setLevel(level=logging.DEBUG)
    time_rotating_file_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    log.addHandler(time_rotating_file_handler)
    return log


def parse_message(message, push_type):
    if push_type == "pushplus":
        return parse(message, template="html")
    else:
        return parse(message, template="markdown")


def pushMessage(message, config):
    if isinstance(config, list):
        for item in config:
            t = item.get("type")
            info(f"消息类型：{t}")
            p = PushSender(t, item.get("key"))
            p.send(parse_message(message, t), title="Bilibili自动签到")
    else:
        t = config.get("type")
        info(f"消息类型：{t}")
        p = PushSender(config.get("type"), config.get("key"))
        p.send(parse_message(message, t), title="Bilibili自动签到")


def bilibiliJob(*args):
    start_time = time.time()
    accounts = json.loads(os.environ.get("MULTI", default="{}"), strict=False)
    push_together = json.loads(os.environ.get("PUSH", default="{}"), strict=False)
    cookie= os.environ.get("BILIBILI_COOKIE", default="{}")

    all_results = []
    for item in accounts:
        item['cookie']=cookie
        obj = BiliBili(**item)
        res = obj.start()
        info(f"[{obj.uid}] bilibili任务执行结果：{res}")
        if res:
            pushMessage(res, push_together)
            # 收集原始数据用于邮件通知
            if hasattr(obj, '_raw_result'):
                all_results.append(obj._raw_result)

    # 计算执行时长
    duration = time.time() - start_time

    # 发送邮件通知
    if all_results:
        try:
            send_bilibili_notification(all_results, duration=duration)
        except Exception as e:
            info(f"邮件通知发送异常: {e}")



if __name__ == "__main__":
    log = build_logger('bili')
    bilibiliJob()
