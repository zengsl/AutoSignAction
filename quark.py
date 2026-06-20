import json
import os
import re
import sys
import time

import requests

from push.tools.util import doSend
from email_notifier import send_quark_notification

# cookie_list = os.getenv("COOKIE_QUARK").split('\n|&&')


# 替代 notify 功能
def send(title, message):
    if not message:
        return
    doSend(title, message)


# 获取环境变量
def get_env():
    # 判断 COOKIE_QUARK是否存在于环境变量
    if "COOKIE_QUARK" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_QUARK'))
    else:
        # 标准日志输出
        print('❌未添加COOKIE_QUARK变量')
        send('夸克自动签到', '❌未添加COOKIE_QUARK变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list

# def get_env():
#     # 判断 COOKIE_QUARK是否存在于环境变量
#     cookie_list = []
#     if "COOKIE_QUARK" in os.environ:
#         # 读取系统变量以 \n 或 && 分割变量
#         cookie_list = re.split('\n|&&', os.environ.get('COOKIE_QUARK'))
#     else:
#         # 标准日志输出
#         print('❌未添加COOKIE_QUARK变量')
#         send('夸克自动签到', '❌未添加COOKIE_QUARK变量')
#         # 脚本退出
#         sys.exit(0)
#
#     return cookie_list


# 其他代码...

class Quark:
    '''
    Quark类封装了签到、领取签到奖励的方法
    '''

    def __init__(self, user_data):
        '''
        初始化方法
        :param user_data: 用户信息，用于后续的请求
        '''
        self.param = user_data
        self.data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data')
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        date = time.localtime()
        now_date = time.strftime("%Y-%m-%d", date)
        self.task_date = now_date
        self.task_result_file_path = os.path.join(self.data_path, f'quark-{now_date}-dailySign.json')
        self.is_complete=False

    def convert_bytes(self, b):
        '''
        将字节转换为 MB GB TB
        :param b: 字节数
        :return: 返回 MB GB TB
        '''
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while b >= 1024 and i < len(units) - 1:
            b /= 1024
            i += 1
        return f"{b:.2f} {units[i]}"

    def get_growth_info(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }
        response = requests.get(url=url, params=querystring).json()
        # print(response)
        if response.get("data"):
            return response["data"]
        else:
            print(f"❌ 获取成长信息接口返回异常: code={response.get('code')}, message={response.get('message')}, status={response.get('status')}")
            return False

    def get_growth_sign(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }
        data = {"sign_cyclic": True}
        response = requests.post(url=url, json=data, params=querystring).json()
        # print(response)
        if response.get("data"):
            return True, response["data"]["sign_daily_reward"]
        else:
            print(f"❌ 签到接口返回异常: code={response.get('code')}, message={response.get('message')}, status={response.get('status')}")
            return False, response.get("message", "未知错误")

    def queryBalance(self):
        '''
        查询抽奖余额
        '''
        url = "https://coral2.quark.cn/currency/v1/queryBalance"
        querystring = {
            "moduleCode": "1f3563d38896438db994f118d4ff53cb",
            "kps": self.param.get('kps'),
        }
        response = requests.get(url=url, params=querystring).json()
        # print(response)
        if response.get("data"):
            return response["data"]["balance"]
        else:
            print(f"❌ 查询抽奖余额接口返回异常: code={response.get('code')}, msg={response.get('msg')}")
            return response.get("msg", "未知错误")

    def do_sign(self):
        '''
        执行签到任务
        :return: 返回一个字符串，包含签到结果
        '''
        if not self.should_run():
            print("不需要签到")
            return ''
        log = ""
        # 每日领空间
        growth_info = self.get_growth_info()
        if growth_info:
            log += (
                f" {'88VIP' if growth_info['88VIP'] else '普通用户'} {self.param.get('user')}\n"
                f"💾 网盘总容量：{self.convert_bytes(growth_info['total_capacity'])}，"
                f"签到累计容量：")
            if "sign_reward" in growth_info['cap_composition']:
                log += f"{self.convert_bytes(growth_info['cap_composition']['sign_reward'])}\n"
            else:
                log += "0 MB\n"
            if growth_info["cap_sign"]["sign_daily"]:
                log += (
                    f"✅ 签到日志: 今日已签到+{self.convert_bytes(growth_info['cap_sign']['sign_daily_reward'])}，"
                    f"连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})\n"
                )
                self.is_complete = True
                self.build_save_data()
            else:
                sign, sign_return = self.get_growth_sign()
                if sign:
                    log += (
                        f"✅ 执行签到: 今日签到+{self.convert_bytes(sign_return)}，"
                        f"连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})\n"
                    )
                    self.is_complete = True
                    self.build_save_data()
                else:
                    log += f"❌ 签到异常: {sign_return}\n"
        else:
            log += f"❌ 签到异常: 获取成长信息失败\n"

        return log

    def should_run(self):
        """是否应该运行"""
        if not os.path.isfile(self.task_result_file_path):
            open(self.task_result_file_path, 'x')
            return True
        with open(self.task_result_file_path) as f:
            data = f.read()
            if not data:
                return True
            return not json.loads(data).get('is_complete')

    def build_save_data(self, **kwargs):
        """构建保持信息"""
        with open(self.task_result_file_path, 'w') as f:
            f.write(json.dumps(self.task_result))

    @property
    def task_result(self):
        """任务结果"""
        return {
            'is_complete': self.is_complete
        }

def quark_main():
    '''
    主函数
    :return: 返回一个字符串，包含签到结果
    '''
    msg = ""
    global cookie_quark
    cookie_quark = get_env()

    print("✅ 检测到共", len(cookie_quark), "个夸克账号\n")

    all_results = []
    has_error = False
    i = 0
    while i < len(cookie_quark):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_quark[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a[0:a.index('=')]: a[a.index('=') + 1:]})
        # print(user_data)
        # 开始任务
        log = f"🙍🏻‍♂️ 第{i + 1}个账号"
        msg += log
        # 登录
        log = Quark(user_data).do_sign()
        if log is None:
            return
        msg += log + "\n"
        all_results.append(log)

        # 检查是否有失败标记
        if "❌" in log:
            has_error = True

        i += 1

    try:
        if has_error:
            send('夸克自动签到', '部分账号签到失败，请查看运行日志')
        else:
            send('夸克自动签到', '成功')
    except Exception as err:
        send('夸克自动签到出现异常', err)
        print('%s\n❌ 错误，请查看运行日志！' % err)

    # 发送邮件通知
    if all_results:
        try:
            send_quark_notification(all_results)
        except Exception as e:
            print(f"邮件通知发送异常: {e}")

    return msg[:-1]




if __name__ == "__main__":
    print("----------夸克网盘开始签到----------")
    quark_main()
    print("----------夸克网盘签到完毕----------")
