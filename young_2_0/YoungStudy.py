import configparser
import pandas as pd
import pymysql
import time
import datetime
import re

""" 设置时间 """
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


""" 清洗列表中的数据格式 """
class ClearFormat:
    # ====== 处理格式 ===========
    normal_str_format_list = []
    reg_str_format_list = []

    def __init__(self):
        # ======================== 处理信息 ========================================================
        cp = configparser.SafeConfigParser()
        cp.read('./conf/properties.conf', encoding="utf-8")
        self.normal_str_format_list = cp.get('clear_format', 'normal_str_list').replace('"', "").split(",")
        del self.normal_str_format_list[0]
        # 读取正则表达式字符串
        self.reg_str_format_list = cp.get('clear_format', 'reg_str_list').replace('"', "").split(",")
        del self.reg_str_format_list[0]

        # 采用配置文件中的格式化字符串

    def conf_clear_name_format(self, name_list):
        new_name_list = []
        for name in name_list:
            # 格式化普通字符串
            if len(self.normal_str_format_list) != 0:
                for str_format in self.normal_str_format_list:
                    name = name.replace(str_format, '')

            # 格式化正则表达式字符串
            if len(self.reg_str_format_list) != 0:
                for reg_format in self.reg_str_format_list:
                    reg = re.compile(reg_format)
                    name = reg.sub("", name)
            # 奖处理完成的字符串放到列表中
            new_name_list.append(name)

        del new_name_list[0]
        return new_name_list

    # 普通的格式化字符串的方式
    def normal_clear_name_format(self, name_list):
        new_name_list = []
        for name in name_list:
            regName = name.replace('软件技术1901', '').replace(' ', '').replace("软件1901", "")
            reg = re.compile('1904301\d{2}')
            name = reg.sub("", regName)
            new_name_list.append(name)
        del new_name_list[0]
        return new_name_list


""" 获取人员列表 """
class GetPeopleList:
    newFileUrl = ""
    list_index = 2
    class_name = ""

    # 初始化操作：读取配置文件信息
    def __init__(self):
        # ======================== 读取文件信息初始化 ==========================================
        cp = configparser.SafeConfigParser()
        cp.read('./conf/properties.conf', encoding="utf-8")
        # ./file/19届·9.27期大学习有效后台数据（周三14：15导出）.xlsx
        self.newFileUrl = "./file/" + cp.get('file_info', 'new_name_file').replace('"', "")
        # 班级所在的列
        self.list_index = int(cp.get('class_info', 'index'))
        self.class_name = cp.get('class_info', 'class_name')

    # 读取xlsx 表中指定的学生的信息
    def get_xlsx_student_list(self):
        df = pd.read_excel(self.newFileUrl, usecols=[self.list_index], names=None)
        df_li = df.values.tolist()
        result = []
        # 去除nan 操作
        for s_li in df_li:
            if type(s_li[0]) == str:
                result.append(s_li[0])
        # del result[0]
        return result

    # 读取mysql 表中指定班级的学生的信息(学生号码和学生姓名)
    def get_mysql_student_list(self):
        new_all_name_list = []
        # 使用cursor()方法创建一个游标对象cursor
        mycursor = ConnectMysql().database.cursor()
        sql = "SELECT student_name,student_email,student_id FROM all_student_info WHERE class_name = " + self.class_name
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        for x in myresult:
            new_all_name_list.append(x)

        return new_all_name_list

    # 从数据库列表中筛选出所有的姓名列表
    def get_all_name_list(self):
        new_all_name_list = []
        for x in self.get_mysql_student_list():
            new_all_name_list.append(x[0])
        return new_all_name_list

    # 从数据库列表中筛选出所有的学号-姓名列表
    def get_all_name_id_dic(self):
        new_all_name_id_dic = {}
        for x in self.get_mysql_student_list():
            new_all_name_id_dic.setdefault(x[2], x[0])
        return new_all_name_id_dic

    # 获取没有完成的人员名单
    def get_not_finish_list(self):
        all_name_list = self.get_all_name_list()
        new_name_list = ClearFormat().conf_clear_name_format(self.get_xlsx_student_list())
        not_finish_list = [x for x in all_name_list if x not in new_name_list]
        return not_finish_list

    # 获取完成的情况
    def get_finish_info(self):
        self.sum_people_num = len(self.get_all_name_list())
        self.finish_people_num = len(self.get_xlsx_student_list()) -1
        self.not_finish_people_num = self.sum_people_num - self.finish_people_num
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        info = {}
        info.setdefault("sum_people_num", self.sum_people_num)
        info.setdefault("finish_people_num", self.finish_people_num)
        info.setdefault("not_finish_people_num", self.not_finish_people_num)
        info.setdefault("time", self.time)
        info.setdefault("class_name", self.class_name)

        info.setdefault("not_finish_list",
                        self.get_not_finish_list())
        return info


""" 将人员信息写入到文件中 """
class OutToFile:
    file = ""

    def __init__(self):
        # ./file/青年大学习未完成名单.txt
        file = open("./file/青大未完成名单.txt", "w+", encoding="utf-8")
        self.file = file

    def info_to_txt(self, info_dic):
        file = self.file
        file.write("班级:" + info_dic["class_name"] + "\n")
        # 写入时间
        file.write("日期:" + info_dic["time"] + "\n")

        file.write("班级总人数:" + str(info_dic['sum_people_num']) + "\t")
        file.write("已完成人数:" + str(info_dic['finish_people_num'] ) + "\t")
        file.write("未完成人数:" + str(info_dic['not_finish_people_num']) + "\n")
        file.write("==============================================================\n")

        print(info_dic["not_finish_list"])
        for stu in info_dic["not_finish_list"]:
            file.write(stu + "\n")


""" 将没有完成的人员写到数据库中 """
class NotFinishPeopleToMySql:
    not_finish_list = []
    sunday = ""
    cursor = ""
    database = ""

    def __init__(self):
        self.not_finish_list = GetPeopleList().get_not_finish_list()
        self.sunday = GetTime().sundayTime
        self.database = ConnectMysql().database
        self.cursor = self.database.cursor()

    def insert_not_finish_list(self):
        for not_finish in self.not_finish_list:
            if not self.is_exit_mysql(not_finish):
                self.insert_to_mysql(not_finish)

    def is_exit_mysql(self, stu_name):
        sql = "select COUNT(*) from not_finish_name where name ='" + stu_name + "' and time =" + self.sunday
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if results[0][0] == 0:
            return False
        else:
            return True

    def insert_to_mysql(self, stu_name):
        sql = "insert into not_finish_name(name, time, is_finish) values ('" + stu_name + "', " + self.sunday + ", 0)"
        self.cursor.execute(sql)
        self.database.commit()


if __name__ == '__main__':
    read = GetPeopleList()

    # 打印人数列表

    # TODO 数据不对，多调用了一次同一个方法，减去了两次第一个数
    print(len(read.get_all_name_list()))
    print(len(read.get_xlsx_student_list()))
    print((read.get_xlsx_student_list()))

    info = read.get_finish_info()
    otf = OutToFile()
    otf.info_to_txt(info)

    # 测试未做列表插入数据库
    tomysql = NotFinishPeopleToMySql()
    tomysql.insert_not_finish_list()
