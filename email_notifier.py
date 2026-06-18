# -*- coding: utf-8 -*-
"""
邮件通知模块
用于发送签到结果到指定邮箱
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Dict, Any


class EmailNotifier:
    """邮件通知类"""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        初始化邮件通知器

        Args:
            smtp_server: SMTP 服务器地址
            smtp_port: SMTP 端口（通常 465 为 SSL，587 为 TLS）
            sender_email: 发件人邮箱
            sender_password: 发件人邮箱密码或授权码
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_text(self, recipient_email: str, subject: str, content: str) -> bool:
        """发送纯文本邮件"""
        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            return self._send(recipient_email, msg)
        except Exception as e:
            print(f'[邮件通知] 构建邮件失败: {e}')
            return False

    def send_html(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """发送 HTML 格式邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            return self._send(recipient_email, msg)
        except Exception as e:
            print(f'[邮件通知] 构建邮件失败: {e}')
            return False

    def send_mixed(self, recipient_email: str, subject: str, text_content: str, html_content: str) -> bool:
        """发送混合格式邮件（同时包含纯文本和 HTML）"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            return self._send(recipient_email, msg)
        except Exception as e:
            print(f'[邮件通知] 构建邮件失败: {e}')
            return False

    def _send(self, recipient_email: str, msg: MIMEMultipart) -> bool:
        """发送邮件"""
        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            print(f'[邮件通知] 邮件发送成功 -> {recipient_email}')
            return True
        except smtplib.SMTPAuthenticationError:
            print(f'[邮件通知] 认证失败: 请检查邮箱密码或授权码')
            return False
        except smtplib.SMTPException as e:
            print(f'[邮件通知] SMTP 错误: {e}')
            return False
        except Exception as e:
            print(f'[邮件通知] 发送异常: {e}')
            return False


def build_bilibili_report_html(results: List[Dict[str, Any]], execution_time: str) -> str:
    """
    构建 Bilibili 签到报告 HTML 内容

    Args:
        results: 签到结果列表，每个元素是 BiliBili.start() 的原始返回值
        execution_time: 执行时间字符串

    Returns:
        HTML 格式的报告内容
    """
    success_list = [r for r in results if r.get('name') != '未登录' and r.get('name') != 'Unkown']
    fail_list = [r for r in results if r.get('name') == '未登录' or r.get('name') == 'Unkown']

    total = len(results)
    success_count = len(success_list)
    fail_count = len(fail_list)

    if fail_count == 0:
        status_color = '#52c41a'
        status_text = f'全部成功 ✨ ({success_count}/{total})'
    elif success_count == 0:
        status_color = '#ff4d4f'
        status_text = f'全部失败 ⚠️ ({fail_count}/{total})'
    else:
        status_color = '#faad14'
        status_text = f'成功 {success_count}，失败 {fail_count}'

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            background: #fff;
            padding: 20px;
            border: 1px solid #e8e8e8;
            border-top: none;
        }}
        .info-box {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background-color: {status_color};
        }}
        .account-card {{
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .account-name {{
            font-size: 18px;
            font-weight: bold;
            color: #1890ff;
            margin-bottom: 10px;
        }}
        .account-info {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 10px;
        }}
        .info-item {{
            background: white;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            border: 1px solid #f0f0f0;
        }}
        .info-label {{
            font-size: 12px;
            color: #999;
        }}
        .info-value {{
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }}
        .task-list {{
            margin-top: 10px;
        }}
        .task-item {{
            padding: 6px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .task-item:last-child {{
            border-bottom: none;
        }}
        .success {{
            color: #52c41a;
        }}
        .fail {{
            color: #ff4d4f;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 0 0 8px 8px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border: 1px solid #e8e8e8;
            border-top: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📺 Bilibili 签到报告</h1>
    </div>
    <div class="content">
        <div class="info-box">
            <strong>执行时间:</strong> {execution_time}<br>
            <strong>签到状态:</strong> <span class="status">{status_text}</span>
        </div>
"""

    for r in results:
        name = r.get('name', '未知')
        level = r.get('level', '-')
        coin = r.get('coin', '-')
        exp = r.get('exp', '-')

        is_fail = name == '未登录' or name == 'Unkown'

        html += f"""
        <div class="account-card">
            <div class="account-name">{'❌' if is_fail else '✅'} {name}</div>
"""
        if is_fail:
            html += f"""
            <p class="fail">签到失败：账号未登录或 Cookie 失效</p>
"""
        else:
            html += f"""
            <div class="account-info">
                <div class="info-item">
                    <div class="info-label">等级</div>
                    <div class="info-value">Lv.{level}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">硬币</div>
                    <div class="info-value">{coin}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">经验</div>
                    <div class="info-value">{exp}</div>
                </div>
            </div>
            <div class="task-list">
"""
            watch = r.get('watch')
            if watch:
                html += f"""
                <div class="task-item">🎬 {watch}</div>
"""

            share = r.get('share')
            if share:
                html += f"""
                <div class="task-item">📤 分享视频成功</div>
"""

            coins = r.get('coins')
            if coins:
                html += f"""
                <div class="task-item">🪙 投币: {', '.join(coins)}</div>
"""

            comics = r.get('comics')
            if comics:
                html += f"""
                <div class="task-item">📖 漫画签到: 连续 {comics} 天</div>
"""

            lb = r.get('lb')
            if lb:
                html += f"""
                <div class="task-item">📺 直播签到: {lb.get('raward', '成功')}</div>
"""

            toCoin = r.get('toCoin')
            if toCoin:
                html += f"""
                <div class="task-item">💰 银瓜子兑换: {toCoin}</div>
"""

            html += """
            </div>
"""

        html += """
        </div>
"""

    html += """
    </div>
    <div class="footer">
        此邮件由 Bilibili 自动签到脚本发送
    </div>
</body>
</html>
"""
    return html


def build_bilibili_report_text(results: List[Dict[str, Any]], execution_time: str) -> str:
    """
    构建 Bilibili 签到报告纯文本内容

    Args:
        results: 签到结果列表
        execution_time: 执行时间字符串

    Returns:
        纯文本格式的报告内容
    """
    success_list = [r for r in results if r.get('name') != '未登录' and r.get('name') != 'Unkown']
    fail_list = [r for r in results if r.get('name') == '未登录' or r.get('name') == 'Unkown']

    lines = [
        'Bilibili 签到报告',
        '=' * 40,
        f'执行时间: {execution_time}',
        ''
    ]

    for r in results:
        name = r.get('name', '未知')
        is_fail = name == '未登录' or name == 'Unkown'

        lines.append(f'{"❌" if is_fail else "✅"} {name}')

        if is_fail:
            lines.append('  签到失败：账号未登录或 Cookie 失效')
        else:
            level = r.get('level', '-')
            coin = r.get('coin', '-')
            exp = r.get('exp', '-')
            lines.append(f'  等级: Lv.{level} | 硬币: {coin} | 经验: {exp}')

            watch = r.get('watch')
            if watch:
                lines.append(f'  🎬 {watch}')

            share = r.get('share')
            if share:
                lines.append(f'  📤 分享视频成功')

            coins = r.get('coins')
            if coins:
                lines.append(f'  🪙 投币: {", ".join(coins)}')

            comics = r.get('comics')
            if comics:
                lines.append(f'  📖 漫画签到: 连续 {comics} 天')

            lb = r.get('lb')
            if lb:
                lines.append(f'  📺 直播签到: {lb.get("raward", "成功")}')

            toCoin = r.get('toCoin')
            if toCoin:
                lines.append(f'  💰 银瓜子兑换: {toCoin}')

        lines.append('')

    lines.append('=' * 40)
    total = len(results)
    success_count = len(success_list)
    fail_count = len(fail_list)

    if fail_count == 0:
        lines.append(f'汇总: 全部成功 ({success_count}/{total})')
    elif success_count == 0:
        lines.append(f'汇总: 全部失败 ({fail_count}/{total})')
    else:
        lines.append(f'汇总: 成功 {success_count}，失败 {fail_count}')

    return '\n'.join(lines)


def build_quark_report_html(results: List[str], execution_time: str) -> str:
    """
    构建夸克网盘签到报告 HTML 内容

    Args:
        results: 签到结果列表，每个元素是 Quark.do_sign() 的返回值字符串
        execution_time: 执行时间字符串

    Returns:
        HTML 格式的报告内容
    """
    success_count = sum(1 for r in results if '✅' in r and '❌' not in r)
    fail_count = len(results) - success_count
    total = len(results)

    if fail_count == 0:
        status_color = '#52c41a'
        status_text = f'全部成功 ✨ ({success_count}/{total})'
    elif success_count == 0:
        status_color = '#ff4d4f'
        status_text = f'全部失败 ⚠️ ({fail_count}/{total})'
    else:
        status_color = '#faad14'
        status_text = f'成功 {success_count}，失败 {fail_count}'

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            background: #fff;
            padding: 20px;
            border: 1px solid #e8e8e8;
            border-top: none;
        }}
        .info-box {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background-color: {status_color};
        }}
        .account-card {{
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
            white-space: pre-line;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 0 0 8px 8px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border: 1px solid #e8e8e8;
            border-top: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>☁️ 夸克网盘签到报告</h1>
    </div>
    <div class="content">
        <div class="info-box">
            <strong>执行时间:</strong> {execution_time}<br>
            <strong>签到状态:</strong> <span class="status">{status_text}</span>
        </div>
"""

    for i, result in enumerate(results, 1):
        html += f"""
        <div class="account-card">
            <strong>🙍🏻‍♂️ 第 {i} 个账号</strong><br>
{result}
        </div>
"""

    html += """
    </div>
    <div class="footer">
        此邮件由夸克网盘自动签到脚本发送
    </div>
</body>
</html>
"""
    return html


def build_quark_report_text(results: List[str], execution_time: str) -> str:
    """
    构建夸克网盘签到报告纯文本内容

    Args:
        results: 签到结果列表
        execution_time: 执行时间字符串

    Returns:
        纯文本格式的报告内容
    """
    success_count = sum(1 for r in results if '✅' in r and '❌' not in r)
    fail_count = len(results) - success_count
    total = len(results)

    lines = [
        '夸克网盘签到报告',
        '=' * 40,
        f'执行时间: {execution_time}',
        ''
    ]

    for i, result in enumerate(results, 1):
        lines.append(f'🙍🏻‍♂️ 第 {i} 个账号')
        lines.append(result)
        lines.append('')

    lines.append('=' * 40)
    if fail_count == 0:
        lines.append(f'汇总: 全部成功 ({success_count}/{total})')
    elif success_count == 0:
        lines.append(f'汇总: 全部失败 ({fail_count}/{total})')
    else:
        lines.append(f'汇总: 成功 {success_count}，失败 {fail_count}')

    return '\n'.join(lines)


def _get_email_config():
    """从环境变量获取邮件配置"""
    smtp_server = os.environ.get('EMAIL_SMTP_SERVER', '')
    smtp_port = int(os.environ.get('EMAIL_SMTP_PORT', '465'))
    sender_email = os.environ.get('EMAIL_SENDER', '')
    sender_password = os.environ.get('EMAIL_PASSWORD', '')
    recipient_emails = os.environ.get('EMAIL_RECIPIENT', '')

    if not all([smtp_server, sender_email, sender_password, recipient_emails]):
        print('[邮件通知] 邮件配置不完整，跳过通知')
        return None

    return {
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'sender_email': sender_email,
        'sender_password': sender_password,
        'recipient_emails': recipient_emails,
    }


def send_bilibili_notification(results: List[Dict[str, Any]], execution_time: Optional[str] = None) -> bool:
    """
    发送 Bilibili 签到通知邮件

    Args:
        results: 签到结果列表，每个元素是 BiliBili.start() 的原始返回值
        execution_time: 执行时间（可选，默认使用当前时间）

    Returns:
        是否发送成功
    """
    config = _get_email_config()
    if not config:
        return False

    if not execution_time:
        execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_content = build_bilibili_report_html(results, execution_time)
    text_content = build_bilibili_report_text(results, execution_time)

    success_list = [r for r in results if r.get('name') != '未登录' and r.get('name') != 'Unkown']
    fail_list = [r for r in results if r.get('name') == '未登录' or r.get('name') == 'Unkown']
    success_count = len(success_list)
    fail_count = len(fail_list)

    if fail_count == 0:
        subject = f'✅ [Bilibili签到] 全部成功 ({success_count}个账号)'
    elif success_count == 0:
        subject = f'❌ [Bilibili签到] 全部失败 ({fail_count}个账号)'
    else:
        subject = f'📋 [Bilibili签到] 成功{success_count}/失败{fail_count}'

    notifier = EmailNotifier(config['smtp_server'], config['smtp_port'], config['sender_email'], config['sender_password'])

    success = True
    for email in config['recipient_emails'].split(','):
        email = email.strip()
        if email:
            if not notifier.send_mixed(email, subject, text_content, html_content):
                success = False

    return success


def send_quark_notification(results: List[str], execution_time: Optional[str] = None) -> bool:
    """
    发送夸克网盘签到通知邮件

    Args:
        results: 签到结果列表，每个元素是 Quark.do_sign() 的返回值字符串
        execution_time: 执行时间（可选，默认使用当前时间）

    Returns:
        是否发送成功
    """
    config = _get_email_config()
    if not config:
        return False

    if not execution_time:
        execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_content = build_quark_report_html(results, execution_time)
    text_content = build_quark_report_text(results, execution_time)

    success_count = sum(1 for r in results if '✅' in r and '❌' not in r)
    fail_count = len(results) - success_count

    if fail_count == 0:
        subject = f'✅ [夸克签到] 全部成功 ({success_count}个账号)'
    elif success_count == 0:
        subject = f'❌ [夸克签到] 全部失败 ({fail_count}个账号)'
    else:
        subject = f'📋 [夸克签到] 成功{success_count}/失败{fail_count}'

    notifier = EmailNotifier(config['smtp_server'], config['smtp_port'], config['sender_email'], config['sender_password'])

    success = True
    for email in config['recipient_emails'].split(','):
        email = email.strip()
        if email:
            if not notifier.send_mixed(email, subject, text_content, html_content):
                success = False

    return success


# 测试入口
if __name__ == '__main__':
    # 测试数据
    test_bilibili_results = [
        {
            'name': '测试用户',
            'level': 5,
            'coin': 100.5,
            'exp': '1000/2000',
            'coins': ['视频A', '视频B'],
            'share': '视频标题',
            'comics': 15,
            'lb': {'raward': '1000银瓜子', 'specialText': ''},
            'watch': '观看视频成功',
            'toCoin': '兑换成功'
        }
    ]

    test_quark_results = [
        " ✅ 签到日志: 今日已签到+10MB，连签进度(3/7)\n💾 网盘总容量：1.5TB，签到累计容量：100MB"
    ]

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print('=== Bilibili HTML 预览 ===')
    print(build_bilibili_report_html(test_bilibili_results, now)[:500] + '...')
    print()

    print('=== Bilibili 纯文本预览 ===')
    print(build_bilibili_report_text(test_bilibili_results, now))
    print()

    print('=== 夸克 HTML 预览 ===')
    print(build_quark_report_html(test_quark_results, now)[:500] + '...')
    print()

    print('=== 夸克 纯文本预览 ===')
    print(build_quark_report_text(test_quark_results, now))
    print()

    if os.environ.get('EMAIL_SMTP_SERVER'):
        print('正在发送测试邮件...')
        send_bilibili_notification(test_bilibili_results)
        send_quark_notification(test_quark_results)
    else:
        print('提示: 设置 EMAIL_* 环境变量后可测试实际发送')
