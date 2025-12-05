import smtplib
import time

from email.mime.text import MIMEText
from email.header import Header


class Mail:
    def __init__(self, mail_host, mail_user, mail_pass, port, mail_from, mail_to, receives):
        # 设置服务器
        self.mail_host = mail_host
        # 用户名
        self.mail_user = mail_user
        # 口令
        self.mail_pass = mail_pass
        self.port = port
        self.mail_from = mail_from
        self.mail_to = mail_to
        self.receives = receives
        # self.log = build_logger()
        # self.log = print

    def send(self, msg, **kwargs):
        return self.send2(kwargs.get("title"), msg, self.mail_from, self.mail_to, self.receives)

    def send2(self, subject, msg, form_header_, to_header, receivers=None):

        if receivers is None:
            receivers = []
        message = MIMEText(msg, 'html', 'utf-8')
        message['From'] = Header(str(f'ddd <{form_header_}>'))
        message['To'] = Header(to_header, 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        for i in range(3):
            try:
                server = smtplib.SMTP_SSL(self.mail_host)  # 在阿里云上python2.7以上需要使用SSL协议
                server.connect(self.mail_host, port=self.port)  # 阿里云25 和80 端口均被使用 465端口使用 SSL协议
                server.login(self.mail_user, self.mail_pass)
                server.sendmail(self.mail_user, receivers, message.as_string())
                server.close()
                # self.log.info("邮件发送成功")
                print("邮件发送成功")
                return 1
            except Exception as e:
                # self.log.error(f" 无法发送邮件; {e}")
                print(f" 无法发送邮件; {e}")
        return 0


if __name__ == '__main__':
    def send_mail(_now_date, _msg, task_name):
        """邮件发送"""
        qq = 'xxx@foxmail.com'
        mail = Mail("smtp.qq.com", 'xxx@foxmail.com', '', 465)
        mail.send2(str(f"测试账号可用"), str(_msg), str(f'ddd <{qq}>'), qq, [qq])

    date = time.localtime()
    formate_time = time.strftime("%Y-%m-%d %H:%M:%S", date)
    send_mail(formate_time, '测试邮件', f"测试账号")
