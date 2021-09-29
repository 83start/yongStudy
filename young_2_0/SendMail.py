import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser
import pymysql
import time
import datetime


class GetTime:
    todayTime = ""
    sundayTime = ""
    weekday = 6

    def __init__(self):
        self.get_today_day()
        self.get_week_day()
        self.get_sunday_time()

    def get_today_day(self):
        self.todayTime = time.strftime("%Y%m%d", time.localtime())

    def get_week_day(self):
        self.weekday = datetime.date.today().weekday()

    def get_sunday_time(self):
        time_cha = 6 - self.weekday
        self.sundayTime = (datetime.date.today() + datetime.timedelta(days=time_cha)).strftime('%Y%m%d')


""" 连接数据库 """


class ConnectMysql:
    # ====== mysql 变量 =======
    host = "localhost"
    user = "root"
    passwd = "root"
    db = "young_study"
    database = ""

    def __init__(self):
        cp = configparser.SafeConfigParser()
        cp.read('./conf/properties.conf', encoding="utf-8")
        self.host = cp.get("mysql_info", "host").replace('"', '')
        self.user = cp.get("mysql_info", "user").replace('"', '')
        self.passwd = cp.get("mysql_info", "passwd").replace('"', '')
        self.db = cp.get("mysql_info", "db").replace('"', '')
        self.database = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)


class GetNotFinishList:
    not_finish_dic = {}
    sunday = ""
    cursor = ""
    database = ""

    def __init__(self):
        self.sunday = GetTime().sundayTime
        self.database = ConnectMysql().database
        self.cursor = self.database.cursor()

    def from_mysql_get_not_finish_dic(self):
        sql = "select name from not_finish_name where time = " + self.sunday + " and is_finish = 0;"
        sql2 = "select student_id ,student_name,student_email from all_student_info where student_name = "
        self.cursor.execute(sql)
        not_finish_tup = self.cursor.fetchall()

        name_list = []
        for not_finish in not_finish_tup:
            name_list.append(not_finish[0])

        email_dic = {}  # stu_info ((190430138, '吴强', '2607280344@qq.com'),)
        # {email:[学号,姓名]}
        for name in name_list:
            sql3 = sql2 + "'" + name + "'"
            self.cursor.execute(sql3)
            stu_info = self.cursor.fetchall()
            print("stu_info", stu_info)
            temp_list = []
            temp_list.append(stu_info[0][2])
            temp_list.append(stu_info[0][1])
            email_dic.setdefault(stu_info[0][0], temp_list)
        print(email_dic)
        return email_dic


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
        message = MIMEText("学号为【" + stu_info_list[0] + "】的" + stu_info_list[1] + "同学，请你在今晚之前完成青年大学习的学习，并反馈你的截图。",
                           'plain', 'utf-8')
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

    def send_to_all(self):
        not_finish_dic = GetNotFinishList().from_mysql_get_not_finish_dic()
        for key in not_finish_dic:
            self.send_one_email(key, not_finish_dic[key])


if __name__ == '__main__':
    SendMail().send_to_all()
