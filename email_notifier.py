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


def build_bilibili_report_html(results: List[Dict[str, Any]], execution_time: str, duration: Optional[float] = None) -> str:
    """
    构建 Bilibili 签到报告 HTML 内容

    Args:
        results: 签到结果列表，每个元素是 BiliBili.start() 的原始返回值
        execution_time: 执行时间字符串
        duration: 执行时长（秒）

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

    # 计算任务统计
    task_stats = {
        'watch': {'success': 0, 'fail': 0},
        'share': {'success': 0, 'fail': 0},
        'coins': {'success': 0, 'fail': 0},
        'comics': {'success': 0, 'fail': 0},
        'lb': {'success': 0, 'fail': 0},
        'toCoin': {'success': 0, 'fail': 0},
    }

    for r in success_list:
        if r.get('watch'):
            task_stats['watch']['success'] += 1
        if r.get('share'):
            task_stats['share']['success'] += 1
        if r.get('coins'):
            task_stats['coins']['success'] += 1
        if r.get('comics'):
            task_stats['comics']['success'] += 1
        if r.get('lb'):
            task_stats['lb']['success'] += 1
        if r.get('toCoin'):
            task_stats['toCoin']['success'] += 1

    duration_text = f'{duration:.1f}秒' if duration else '未知'

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
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .info-row:last-child {{
            margin-bottom: 0;
        }}
        .info-label {{
            color: #666;
        }}
        .info-value {{
            font-weight: bold;
        }}
        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background-color: {status_color};
        }}
        .stats-box {{
            background: #e6f7ff;
            border: 1px solid #91d5ff;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .stats-title {{
            font-weight: bold;
            color: #1890ff;
            margin-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }}
        .stat-item {{
            text-align: center;
            padding: 8px;
            background: white;
            border-radius: 4px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
        }}
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1890ff;
        }}
        .account-card {{
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .account-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .account-name {{
            font-size: 18px;
            font-weight: bold;
            color: #1890ff;
        }}
        .account-uid {{
            font-size: 12px;
            color: #999;
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 4px;
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
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: center;
        }}
        .task-item:last-child {{
            border-bottom: none;
        }}
        .task-icon {{
            margin-right: 8px;
            font-size: 16px;
        }}
        .task-text {{
            flex: 1;
        }}
        .task-status {{
            font-size: 12px;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .task-success {{
            background: #f6ffed;
            color: #52c41a;
            border: 1px solid #b7eb8f;
        }}
        .task-fail {{
            background: #fff2f0;
            color: #ff4d4f;
            border: 1px solid #ffccc7;
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
            <div class="info-row">
                <span class="info-label">执行时间</span>
                <span class="info-value">{execution_time}</span>
            </div>
            <div class="info-row">
                <span class="info-label">执行时长</span>
                <span class="info-value">{duration_text}</span>
            </div>
            <div class="info-row">
                <span class="info-label">签到状态</span>
                <span class="status">{status_text}</span>
            </div>
        </div>
"""

    # 添加任务统计（只有成功账号时显示）
    if success_list:
        html += f"""
        <div class="stats-box">
            <div class="stats-title">📊 任务执行统计</div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">观看视频</div>
                    <div class="stat-value">{task_stats['watch']['success']}/{len(success_list)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">分享视频</div>
                    <div class="stat-value">{task_stats['share']['success']}/{len(success_list)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">投币</div>
                    <div class="stat-value">{task_stats['coins']['success']}/{len(success_list)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">漫画签到</div>
                    <div class="stat-value">{task_stats['comics']['success']}/{len(success_list)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">直播签到</div>
                    <div class="stat-value">{task_stats['lb']['success']}/{len(success_list)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">银瓜子兑换</div>
                    <div class="stat-value">{task_stats['toCoin']['success']}/{len(success_list)}</div>
                </div>
            </div>
        </div>
"""

    for r in results:
        name = r.get('name', '未知')
        uid = r.get('uid', '')
        level = r.get('level', '-')
        coin = r.get('coin', '-')
        exp = r.get('exp', '-')

        is_fail = name == '未登录' or name == 'Unkown'

        html += f"""
        <div class="account-card">
            <div class="account-header">
                <div class="account-name">{'❌' if is_fail else '✅'} {name}</div>
                {'<div class="account-uid">UID: ' + uid + '</div>' if uid else ''}
            </div>
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
                <div class="task-item">
                    <span class="task-icon">🎬</span>
                    <span class="task-text">{watch}</span>
                    <span class="task-status task-success">成功</span>
                </div>
"""
            else:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">🎬</span>
                    <span class="task-text">观看视频</span>
                    <span class="task-status task-fail">失败</span>
                </div>
"""

            share = r.get('share')
            if share:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">📤</span>
                    <span class="task-text">分享视频: {share}</span>
                    <span class="task-status task-success">成功</span>
                </div>
"""
            else:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">📤</span>
                    <span class="task-text">分享视频</span>
                    <span class="task-status task-fail">失败</span>
                </div>
"""

            coins = r.get('coins')
            if coins:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">🪙</span>
                    <span class="task-text">投币: {', '.join(coins)}</span>
                    <span class="task-status task-success">成功</span>
                </div>
"""
            else:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">🪙</span>
                    <span class="task-text">投币</span>
                    <span class="task-status task-fail">失败</span>
                </div>
"""

            comics = r.get('comics')
            if comics:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">📖</span>
                    <span class="task-text">漫画签到: 连续 {comics} 天</span>
                    <span class="task-status task-success">成功</span>
                </div>
"""
            else:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">📖</span>
                    <span class="task-text">漫画签到</span>
                    <span class="task-status task-fail">失败</span>
                </div>
"""

            lb = r.get('lb')
            if lb:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">📺</span>
                    <span class="task-text">直播签到: {lb.get('raward', '成功')}</span>
                    <span class="task-status task-success">成功</span>
                </div>
"""
            else:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">📺</span>
                    <span class="task-text">直播签到</span>
                    <span class="task-status task-fail">失败</span>
                </div>
"""

            toCoin = r.get('toCoin')
            if toCoin:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">💰</span>
                    <span class="task-text">银瓜子兑换: {toCoin}</span>
                    <span class="task-status task-success">成功</span>
                </div>
"""
            else:
                html += f"""
                <div class="task-item">
                    <span class="task-icon">💰</span>
                    <span class="task-text">银瓜子兑换</span>
                    <span class="task-status task-fail">失败</span>
                </div>
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


def build_bilibili_report_text(results: List[Dict[str, Any]], execution_time: str, duration: Optional[float] = None) -> str:
    """
    构建 Bilibili 签到报告纯文本内容

    Args:
        results: 签到结果列表
        execution_time: 执行时间字符串
        duration: 执行时长（秒）

    Returns:
        纯文本格式的报告内容
    """
    success_list = [r for r in results if r.get('name') != '未登录' and r.get('name') != 'Unkown']
    fail_list = [r for r in results if r.get('name') == '未登录' or r.get('name') == 'Unkown']

    duration_text = f'{duration:.1f}秒' if duration else '未知'

    lines = [
        'Bilibili 签到报告',
        '=' * 40,
        f'执行时间: {execution_time}',
        f'执行时长: {duration_text}',
        ''
    ]

    # 任务统计
    if success_list:
        task_stats = {
            'watch': sum(1 for r in success_list if r.get('watch')),
            'share': sum(1 for r in success_list if r.get('share')),
            'coins': sum(1 for r in success_list if r.get('coins')),
            'comics': sum(1 for r in success_list if r.get('comics')),
            'lb': sum(1 for r in success_list if r.get('lb')),
            'toCoin': sum(1 for r in success_list if r.get('toCoin')),
        }
        lines.append('📊 任务执行统计:')
        lines.append(f'  观看视频: {task_stats["watch"]}/{len(success_list)}')
        lines.append(f'  分享视频: {task_stats["share"]}/{len(success_list)}')
        lines.append(f'  投币: {task_stats["coins"]}/{len(success_list)}')
        lines.append(f'  漫画签到: {task_stats["comics"]}/{len(success_list)}')
        lines.append(f'  直播签到: {task_stats["lb"]}/{len(success_list)}')
        lines.append(f'  银瓜子兑换: {task_stats["toCoin"]}/{len(success_list)}')
        lines.append('')

    for r in results:
        name = r.get('name', '未知')
        uid = r.get('uid', '')
        is_fail = name == '未登录' or name == 'Unkown'

        uid_text = f' (UID: {uid})' if uid else ''
        lines.append(f'{"❌" if is_fail else "✅"} {name}{uid_text}')

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
            else:
                lines.append(f'  🎬 观看视频: 失败')

            share = r.get('share')
            if share:
                lines.append(f'  📤 分享视频: {share}')
            else:
                lines.append(f'  📤 分享视频: 失败')

            coins = r.get('coins')
            if coins:
                lines.append(f'  🪙 投币: {", ".join(coins)}')
            else:
                lines.append(f'  🪙 投币: 失败')

            comics = r.get('comics')
            if comics:
                lines.append(f'  📖 漫画签到: 连续 {comics} 天')
            else:
                lines.append(f'  📖 漫画签到: 失败')

            lb = r.get('lb')
            if lb:
                lines.append(f'  📺 直播签到: {lb.get("raward", "成功")}')
            else:
                lines.append(f'  📺 直播签到: 失败')

            toCoin = r.get('toCoin')
            if toCoin:
                lines.append(f'  💰 银瓜子兑换: {toCoin}')
            else:
                lines.append(f'  💰 银瓜子兑换: 失败')

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


def build_quark_report_html(results: List[str], execution_time: str, duration: Optional[float] = None) -> str:
    """
    构建夸克网盘签到报告 HTML 内容

    Args:
        results: 签到结果列表，每个元素是 Quark.do_sign() 的返回值字符串
        execution_time: 执行时间字符串
        duration: 执行时长（秒）

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

    duration_text = f'{duration:.1f}秒' if duration else '未知'

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
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .info-row:last-child {{
            margin-bottom: 0;
        }}
        .info-label {{
            color: #666;
        }}
        .info-value {{
            font-weight: bold;
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
        .account-header {{
            font-weight: bold;
            color: #1890ff;
            margin-bottom: 10px;
            font-size: 16px;
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
            <div class="info-row">
                <span class="info-label">执行时间</span>
                <span class="info-value">{execution_time}</span>
            </div>
            <div class="info-row">
                <span class="info-label">执行时长</span>
                <span class="info-value">{duration_text}</span>
            </div>
            <div class="info-row">
                <span class="info-label">签到状态</span>
                <span class="status">{status_text}</span>
            </div>
        </div>
"""

    for i, result in enumerate(results, 1):
        html += f"""
        <div class="account-card">
            <div class="account-header">🙍🏻‍♂️ 第 {i} 个账号</div>
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


def build_quark_report_text(results: List[str], execution_time: str, duration: Optional[float] = None) -> str:
    """
    构建夸克网盘签到报告纯文本内容

    Args:
        results: 签到结果列表
        execution_time: 执行时间字符串
        duration: 执行时长（秒）

    Returns:
        纯文本格式的报告内容
    """
    success_count = sum(1 for r in results if '✅' in r and '❌' not in r)
    fail_count = len(results) - success_count
    total = len(results)

    duration_text = f'{duration:.1f}秒' if duration else '未知'

    lines = [
        '夸克网盘签到报告',
        '=' * 40,
        f'执行时间: {execution_time}',
        f'执行时长: {duration_text}',
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


def send_bilibili_notification(results: List[Dict[str, Any]], execution_time: Optional[str] = None, duration: Optional[float] = None) -> bool:
    """
    发送 Bilibili 签到通知邮件

    Args:
        results: 签到结果列表，每个元素是 BiliBili.start() 的原始返回值
        execution_time: 执行时间（可选，默认使用当前时间）
        duration: 执行时长（秒）

    Returns:
        是否发送成功
    """
    config = _get_email_config()
    if not config:
        return False

    if not execution_time:
        execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_content = build_bilibili_report_html(results, execution_time, duration)
    text_content = build_bilibili_report_text(results, execution_time, duration)

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


def send_quark_notification(results: List[str], execution_time: Optional[str] = None, duration: Optional[float] = None) -> bool:
    """
    发送夸克网盘签到通知邮件

    Args:
        results: 签到结果列表，每个元素是 Quark.do_sign() 的返回值字符串
        execution_time: 执行时间（可选，默认使用当前时间）
        duration: 执行时长（秒）

    Returns:
        是否发送成功
    """
    config = _get_email_config()
    if not config:
        return False

    if not execution_time:
        execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_content = build_quark_report_html(results, execution_time, duration)
    text_content = build_quark_report_text(results, execution_time, duration)

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
