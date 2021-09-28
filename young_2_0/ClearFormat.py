# 数据清洗类
import re
import configparser


class ClearFormat:
    normal_str_format_list = []
    reg_str_format_list = []

    # 初始化，读取配置文件
    def __init__(self):
        cp = configparser.SafeConfigParser()
        cp.read('./conf/properties.conf', encoding="utf-8")
        # 读取普通字符串
        self.normal_str_format_list = cp.get('clear_format', 'normal_str_list').replace('"', "").split(",")
        del self.normal_str_format_list[0]
        # 读取正则表达式字符串
        self.reg_str_format_list = cp.get('clear_format', 'reg_str_list').replace('"', "").split(",")
        del self.reg_str_format_list[0]

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


if __name__ == '__main__':
    name_list = ['软件1901团支部', '软件技术1901郑继红', '软件技术1901张文競', '软件技术1901张瑞元', '软件技术1901徐雪晴', '软件技术1901刘宇恒', '软件技术1901花进',
                 '软件技术1901洪信望', '软件技术1901何瑞睿', '软件技术1901 杨帆', '软件技术1901 胡枫', '软件技术1901 韩信', '软件技术1901 曹俊',
                 '软件技术1901  吴航', '软件1901朱子涵', '软件1901杨蔚', '软件1901邢孙浩', '软件1901王晨璐', '软件1901谈青松', '软件1901彭蒙蒙',
                 '软件1901廖苏', '软件1901樊英杰', '软件1901丁浩轩', '软件1901陈楠', '软件1901 朱静悦', '软件1901 俞潜卓', '软件1901 蒋欢',
                 '软件1901 何承政', '软件1901 曹耀雷', '软件1901 蔡昊', '软件1901 190430105周雪', '软件1901  张国超', '软件1901  陆妍瑞',
                 '软件1901吕勇辉', '软件1901吴强', '软件1901张恩旭', '软件1901朱远军']

    cf = ClearFormat()
    print(cf.reg_str_format_list)
    print(cf.normal_str_format_list)
    new_name_list0 = cf.normal_clear_name_format(name_list)
    new_name_list1 = cf.conf_clear_name_format(name_list)

    print(new_name_list0)
    print(new_name_list1)
