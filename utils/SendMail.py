import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from django.conf import settings


class SendMail:
    def __init__(self, email_dict):
        self.to_mail = email_dict["to_mail"]
        self.sub = email_dict["sub"]
        self.smtp_server = 'smtp.exmail.qq.com'
        self.from_mail = 'deploy@isesol.com'
        self.mail_pass = 'q03TjvSh'
        self.content = email_dict["content"]

    # 格式化邮件地址
    @staticmethod
    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_mail(self):
        msg = MIMEMultipart()
        # Header对中文进行转码
        msg['From'] = self.format_addr('发布邮箱 <%s>' % self.from_mail)
        # msg['To'] = ','.join(self.to_mail)
        msg['To'] = Header(self.to_mail, 'utf-8').encode()
        msg['Subject'] = Header(self.sub, 'utf-8').encode()
        msg.attach(MIMEText('您的密码即将过期，请登陆https://opsre2.i5sesol.com , 或在登陆页面进行密码重置.', 'plain', 'utf-8'))
        try:
            s = smtplib.SMTP_SSL(self.smtp_server, 465)
            s.login(self.from_mail, self.mail_pass)
            s.sendmail(self.from_mail, self.to_mail, msg.as_string())  # as_string()把MIMEText对象变成str
            s.close()
            return {"code": "sucess", "msg": "邮件发送成功."}
        except smtplib.SMTPException as e:
            print(e)
            return {"code": "error", "msg": "邮件发送失败."}

    def order_send_mail(self):
        if self.content['type'] == 'deploy':
            temp_file = os.path.join(settings.BASE_DIR, 'templates/order.html')
        elif self.content['type'] == 'local':
            temp_file = os.path.join(settings.BASE_DIR, 'templates/localOrder.html')
        else:
            temp_file = os.path.join(settings.BASE_DIR, 'templates/opsOrder.html')
        with open(temp_file, 'rt', encoding='utf-8') as f:
            html = f.read()
        html = html.format(**self.content)
        # 构造一个MIMEMultipart对象代表邮件本身
        msg = MIMEMultipart()
        # Header对中文进行转码
        msg['From'] = self.format_addr('发布邮箱 <%s>' % self.from_mail)
        msg['To'] = ','.join(self.to_mail)
        msg['Subject'] = Header(self.content['sub'], 'utf-8').encode()
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        try:
            s = smtplib.SMTP_SSL(self.smtp_server, 465)
            s.login(self.from_mail, self.mail_pass)
            s.sendmail(self.from_mail, self.to_mail, msg.as_string())  # as_string()把MIMEText对象变成str
            s.close()
        except smtplib.SMTPException as e:
            print(e)
