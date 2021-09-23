import pandas as pd
import time
import configparser


oldFileUrl = ""
newFileUrl = ""
list_index = 2

# 获取配置文件的信息c
def get_properties_info():
    global oldFileUrl , newFileUrl ,list_index
    cp = configparser.SafeConfigParser()
    cp.read('./conf/properties.conf',encoding="utf-8")
    oldFileUrl = "./conf/" + cp.get('fileName', 'all_name_file').replace('"',"")
    newFileUrl = "./conf/" + cp.get('fileName', 'new_name_file').replace('"',"")
    list_index = int(cp.get('class', 'index'))
    print(oldFileUrl)
    print(type(list_index))



# 获取第一行的班级信息
def getHeadName():
    df = pd.read_excel(oldFileUrl,usecols=[list_index],names=None)
    df_li = df.values.tolist()
    return df_li[0][0]


# 读取excel 中的指定一列并保存到列表中
def excel_one_line_to_list(fileUrl):
    df = pd.read_excel(fileUrl,usecols=[list_index],names=None)

    df_li = df.values.tolist()
    result = []
    # 去除nan 操作
    for s_li in df_li:
        # print(type(s_li[0]))
        # print(s_li[0])
        if(type(s_li[0]) == str):
            # 处理字符串
            ## 处理正则表达式
            name = s_li[0].replace('软件技术1901','').replace(' ', '').replace("软件1901","")
            result.append(name)
    # 删除班级信息
    del result[0]
    return result

# 筛选出在没有完成的人
def not_finish(oldResult,newResult):
    not_finish_list = [x for x in oldResult if x not in newResult]
    return not_finish_list

# 获取完成的信息
def get_info():
    oldResult = excel_one_line_to_list(oldFileUrl)
    newResult = excel_one_line_to_list(newFileUrl)
    info = {}
    # 先获取班级的总人数
    all_people_num = len(oldResult)
    finish_people_num = len(newResult)
    not_finish_people_num = all_people_num - finish_people_num

    info.setdefault("all_people_num",all_people_num)
    info.setdefault("finish_people_num", finish_people_num)
    info.setdefault("not_finish_people_num", not_finish_people_num)

    return info



# 将没有完成的人的名字打印到txt 文件中
def out_to_txt(not_finish_list):
    className = getHeadName()
    fileName = "./conf/" + className + "青大未完成名单.txt"
    file = open(fileName, "w+",encoding="utf-8")


    # 写入班级信息
    file.write("班级:" + className + "\n")
    # 写入时间
    file.write("日期:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+ "\n")
    # 写入信息
    info = get_info()
    file.write("班级总人数:" + str(info['all_people_num']) + "\t")
    file.write("已完成人数:" + str(info['finish_people_num']) + "\t")
    file.write("未完成人数:" + str(info['not_finish_people_num']) + "\n")

    # 写入没有完成人的名字

    file.write("==================================== 未完成人员名单 ==================================== \n")
    for people in not_finish_list:
        file.write(people + "\n")



if __name__ == '__main__':
    get_properties_info()
    old_people_list = excel_one_line_to_list(oldFileUrl)
    new_people_list = excel_one_line_to_list(newFileUrl)
    not_finish_list = not_finish(old_people_list,new_people_list)

    out_to_txt(not_finish_list)

