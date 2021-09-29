import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser


class SendMail:
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "1308129550@qq.com"  # 用户名
    mail_pass = "tjwelqulkqpjhiai"  # 口令
    sender = '1308129550@qq.com'
    subject = "学习新思想,争做新青年"
    from_header = "软件技术1901团支部"

    def __init__(self):
        cp = configparser.SafeConfigParser()
        cp.read('./conf/properties.conf', encoding="utf-8")
        self.mail_host = cp.get("email_info", "host").replace('"', '')
        self.mail_user = cp.get("email_info", "user").replace('"', '')
        self.mail_pass = cp.get("email_info", "pass").replace('"', '')
        self.sender = cp.get("email_info", "sender").replace('"', '')
        self.subject = cp.get("email_info", "subject").replace('"', '')
        self.from_header = cp.get("email_info", "from_header").replace('"', '')

    def send_one_email(self, email, stu_info_list):
        receivers = []
        receivers.append(email)
        # 设置文章内容
        message = MIMEText("学号为【" +stu_info_list[0]+"】的" +stu_info_list[1]+"同学，请你在今晚之前完成青年大学习的学习，并反馈你的截图。", 'plain', 'utf-8')
        # 设置邮件标题
        message['Subject'] = Header(self.subject, 'utf-8')
        # 设置邮件的发件人姓名
        message['From'] = Header(self.from_header, 'utf-8')
        message['To'] = Header(str(stu_info_list), 'utf-8')

        smtpObj = smtplib.SMTP()
        smtpObj.connect(self.mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(self.mail_user, self.mail_pass)
        smtpObj.sendmail(self.sender, receivers, message.as_string())
        print("邮件发送成功")


if __name__ == '__main__':
    SendMail().send_one_email("1308129550@qq.com",["190430132","曹俊"])
