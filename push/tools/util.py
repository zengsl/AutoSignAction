# coding=utf-8
import json
import logging
import os
from logging import handlers

from bs4 import BeautifulSoup

from push import parse, Qmsg
from push.push import Mail


def get_chapter_nodes(soup):
    """获取章节节点"""
    return soup.select(".chapter-content>.chapter-ul>li")


def get_content_body(soup):
    """获取章节节点"""
    return soup.select_one(".box-body.nvl-content")


def is_login(soap):
    """检查是否登录"""
    return soap.select_one("#loginb input[name='password']")


def change_response_to_dom(response):
    """把response 转换为dom"""
    return BeautifulSoup(response.text, 'lxml')


def build_logger():
    uname = os.environ.get('MASIRO_USER_NAME')
    if not uname:
        uname = 'RedFlag'
    base_name = os.path.join("logs", uname)
    log = logging.getLogger(base_name)
    # os.system("ls -al ~")
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


def build_novel_cover_content(book_title, describe):
    """构建封面正文"""
    return f'<div align="center"><h1>{book_title}</h1><p><img src="images/cover.jpg" ' \
           f'></image></p></div> <br/><br/><p>{describe}</p>'


def create_path_if_not_exist(file_path):
    """ 不存在目录时创建 """
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def build_cookie(response):
    """构建cookie并设置"""
    cookies = response.cookies.items()
    cookie = ''
    for name, value in cookies:
        cookie += '{0}={1};'.format(name, value)
    return cookie


def dump_json_to_file(file_name, data):
    """保持文件信息"""
    with open(file_name) as f:
        f.write(json.dumps(data, ensure_ascii=False))


def delete_file(file_path):
    """删除书"""
    if os.path.isfile(file_path):
        os.remove(file_path)


def doSend(title, message):
    print(f"{title}: {message}")
    if type(message) == str:
        message = [{'h1': {'content': title}}, {'txt': {'content': message}}]
    push_together = json.loads(os.environ.get("PUSH", default="{}"), strict=False)
    if not push_together or not push_together['key']:
        """不发送消息"""
    else:
        parse_msg = parse(message, template="markdown")
        email_config = json.loads(push_together['key'])
        print(f"消息接收人列表：{email_config['receives']} {type(email_config['receives'])}")

        # 固定发送邮件
        Mail(email_config['host'], email_config['user'], email_config['pass'], email_config['port']).send2(parse_msg,
                                                                                                           title=title)
        # Qmsg(push_together['key']).send(parse_msg, title=title)
