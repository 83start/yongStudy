import configparser
import pandas as pd
import pymysql
import time
import re


class GetPeopleList:
    newFileUrl = ""
    list_index = 2
    class_name = ""
    # ====== mysql 变量 =======
    host = "localhost"
    user = "root"
    passwd = "root"
    db = "young_study"
    database = ""
    # ====== 完成的信息 ========
    sum_people_num = 0
    finish_people_num = 0
    not_finish_people_num = 0
    time = ""
    # ====== 处理格式 ===========
    normal_str_format_list = []
    reg_str_format_list = []

    # 初始化操作：读取配置文件信息
    def __init__(self):
        # ======================== 读取文件信息初始化 ==========================================
        cp = configparser.SafeConfigParser()
        cp.read('./conf/properties.conf', encoding="utf-8")
        self.newFileUrl = "./conf/" + cp.get('file_info', 'new_name_file').replace('"', "")
        self.list_index = int(cp.get('class_info', 'index'))
        self.class_name = cp.get('class_info', 'class_name')
        # ======================== 读取数据库数据 ============================================
        self.host = cp.get("mysql_info", "host").replace('"', '')
        self.user = cp.get("mysql_info", "user").replace('"', '')
        self.passwd = cp.get("mysql_info", "passwd").replace('"', '')
        self.db = cp.get("mysql_info", "db").replace('"', '')
        self.database = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
        # ======================== 处理信息 ========================================================
        self.normal_str_format_list = cp.get('clear_format', 'normal_str_list').replace('"', "").split(",")
        del self.normal_str_format_list[0]
        # 读取正则表达式字符串
        self.reg_str_format_list = cp.get('clear_format', 'reg_str_list').replace('"', "").split(",")
        del self.reg_str_format_list[0]

    # 读取xlsx 表中指定的学生的信息
    def get_xlsx_student_list(self):
        df = pd.read_excel(self.newFileUrl, usecols=[self.list_index], names=None)
        df_li = df.values.tolist()
        result = []
        # 去除nan 操作
        for s_li in df_li:
            if type(s_li[0]) == str:
                result.append(s_li[0])
        return result

    # 读取mysql 表中指定班级的学生的信息
    def get_mysql_student_list(self):
        new_all_name_list = []
        # 使用cursor()方法创建一个游标对象cursor
        mycursor = self.database.cursor()
        sql = "SELECT student_name FROM all_student_info WHERE class_name = " + self.class_name
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        for x in myresult:
            new_all_name_list.append(x[0])

        return new_all_name_list

    # 获取没有完成的人员名单
    def get_not_finish_list(self, all_name_list, new_name_list):
        not_finish_list = [x for x in all_name_list if x not in new_name_list]
        return not_finish_list

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

    # 获取完成的情况
    def get_finish_info(self):

        self.sum_people_num = len(self.get_mysql_student_list())
        self.finish_people_num = len(self.get_xlsx_student_list())
        self.not_finish_people_num = self.sum_people_num - self.finish_people_num
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        info = {}
        info.setdefault("sum_people_num", self.sum_people_num)
        info.setdefault("finish_people_num", self.finish_people_num)
        info.setdefault("not_finish_people_num", self.not_finish_people_num)
        info.setdefault("time", self.time)
        info.setdefault("class_name", self.class_name)
        all_name = self.get_mysql_student_list()
        new_name = self.conf_clear_name_format(self.get_xlsx_student_list())
        info.setdefault("not_finish_list",
                        self.get_not_finish_list(all_name, new_name))
        return info


class OutToFile:
    file = ""

    def __init__(self):
        file = open("./conf/青大未完成名单.txt", "w+", encoding="utf-8")
        self.file = file

    def info_to_txt(self, info_dic):
        file = self.file
        file.write("班级:" + info_dic["class_name"] + "\n")
        # 写入时间
        file.write("日期:" + info_dic["time"] + "\n")

        file.write("班级总人数:" + str(info_dic['sum_people_num']) + "\t")
        file.write("已完成人数:" + str(info_dic['finish_people_num']) + "\t")
        file.write("未完成人数:" + str(info_dic['not_finish_people_num']) + "\n")
        file.write("==============================================================\n")

        print(info_dic["not_finish_list"])
        for stu in info_dic["not_finish_list"]:
            file.write(stu + "\n")

class GetEmailList:

class SendEmail:



if __name__ == '__main__':
    read = GetPeopleList()
    # print(read.newFileUrl)
    # print(read.list_index)
    # student_list = read.get_xlsx_student_list()
    # print(student_list)

    # print(read.get_mysql_student_list())
    # print(read.get_xlsx_student_list())
    # new_name_list = ['郑继红', '张文競', '张瑞元', '徐雪晴', '刘宇恒', '花进', '洪信望', '何瑞睿', '杨帆', '胡枫', '韩信', '曹俊', '吴航', '朱子涵', '杨蔚',
    #                  '邢孙浩', '王晨璐', '谈青松', '彭蒙蒙', '廖苏', '樊英杰', '丁浩轩', '陈楠', '朱静悦', '俞潜卓', '蒋欢', '何承政', '曹耀雷', '蔡昊', '周雪',
    #                  '张国超', '陆妍瑞', '吕勇辉', '吴强', '张恩旭', '朱远军']
    # all_name_list = ['韩信', '管永洋', '朱静悦', '郑继红', '廖苏', '胡枫', '周雪', '徐雪晴', '陆妍瑞', '张文競', '何瑞睿', '王晨璐', '蔡昊', '蒋欢', '张瑞元',
    #                  '陈楠', '花进', '杨轩', '邢孙浩', '曹耀雷', '张国超', '吕勇辉', '刘宇恒', '孙浩轩', '谈青松', '朱子涵', '梁义亮', '何承政', '彭蒙蒙',
    #                  '王皓然', '俞潜卓', '曹俊', '杨蔚', '吴航', '洪信望', '张恩旭', '杨帆', '吴强', '樊英杰', '朱远军', '丁浩轩']
    #
    # print(read.get_not_finish_list(all_name_list, new_name_list))

    info = read.get_finish_info()
    otf = OutToFile()
    otf.info_to_txt(info)
