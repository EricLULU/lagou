import requests
#from selenium import webdriver  
from bs4 import BeautifulSoup
from urllib.parse import quote   #导入编码模块
from time import ctime, sleep, time
import multiprocessing
import csv
import json
import random
import pymongo

"""
1. 需求分析
需要爬去的字段：
（1）职位名称
（2）公司名称
（3）薪资
（4）发布时间

（5）城市 是可以自己来控制的。在url中来控制的

功能分析：
（1）构造url 链接： 控制城市，分页
（2）解析 json 格式：获取需求的信息
（3）存储： 利用参 csv 来存储信息
           存储的格式： 地区：{职位名称，薪资，发布时间}
           利用mongodb 来存储
 
"""

#信息的获取，并返回为json数据
#构造 url
def downloader():  
    headers={'Cookie':'user_trace_token=20180617062143-a2c67f89-f721-42a0-a431-0713866d0fc1; __guid=237742470.3953059058839704600.1529187726497.5256;\
    LGUID=20180617062145-a70aea81-71b3-11e8-a55c-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD;\
    JSESSIONID=ABAAABAAAIAACBIA653C35B2B23133DCDB86365CEC619AE; PRE_UTM=; PRE_HOST=; PRE_SITE=;\
    PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_pythonpytho%25E7%2588%25AC%25E8%2599%25AB%3Fcity%3D%25E5%2585%25A8%25E5%259B%25BD;\
    TG-TRACK-CODE=search_code; X_MIDDLE_TOKEN=8a8c6419e33ae49c13de4c9881b4eb1e; X_HTTP_TOKEN=5dd639be7b63288ce718c96fdd4a0035;\
    _ga=GA1.2.1060168094.1529187728; _gid=GA1.2.1053446384.1529187728; _gat=1;\
    Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1529190520,1529198463,1529212181,1529212712;\
    Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1529225935; LGSID=20180617164003-0752289a-720a-11e8-a8bc-525400f775ce;\
    LGRID=20180617165832-9c78c400-720c-11e8-a8bf-525400f775ce; SEARCH_ID=1dab13db9fc14397a080b2d8a32b7f27; monitor_count=70',
    'Host':'www.lagou.com',
    'Origin':'https://www.lagou.com',
    'Referer':'https://www.lagou.com/jobs/list_python%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput=',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'}
    
    city_list = ['北京', '上海', '深圳', '广州','杭州','成都','南京','武汉','西安','厦门','长沙','苏州','天津']
    position_list=['python爬虫',]                    #'python数据分析']    #职位列表

    for city in city_list:
        save_single_info(city)           #写入城市信息
        print("I am in {}".format(city))
        for position in position_list:

            url = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"
            #获取职位页数的链接
            url_page = "https://www.lagou.com/jobs/list_{}?city={}".format(position, city)

            #获取职位页码的总页数
            r = requests.post(url_page, headers=headers)
            doc = BeautifulSoup(r.text, 'lxml')
            page_count = int(doc.find(class_='span totalNum').string)
            #职位数目的获取

            #职位页 遍历
            for page in range(1,page_count+1):

                if page == 1:
                    flag = 'true'
                else:
                    flag = 'false'

                data = {
                    'first':flag,
                    'pn':page,
                    'kd':position,
                    }
                time_sleep = random.random()
                sleep(time_sleep*10)
                response = requests.post(url, headers = headers, data= data, timeout=10)
                data= response.json()
                html_parse(data)   #送到了解析函数



def html_parse(item):
    """
        网页解析
    """
    info = item.get('content')
    p_lsit = info.get('positionResult').get('result')
    print(len(p_lsit))
    for p in p_lsit:
        result_item = {
            "positionName": p.get("positionName"),
            "salary": p.get("salary"),
            "workYear": p.get('workYear'),
        }
        save_to_mongo(result_item)      #将结果存储到mongodb中
        result_save(result_item)        #将结果存储到csv中
 



#字典信息存储
def result_save(result_item):
    print("csv is working")
    with open('lagou.csv','a',newline='',encoding='utf-8') as csvfile:   #打开一个csv文件，用于存储
        fieldnames=['positionName','salary','workYear']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writerow(result_item)


#城市信息存储
def save_single_info(info):
    print("csv is working")
    with open('lagou.csv','a',newline='',encoding='utf-8') as csvfile:
        writer=csv.writer(csvfile)
        if type(info) == list:
            writer.writerow(info)
        else:
            writer.writerow([info])


def save_to_mongo(data):
    #连接数据库

    client = pymongo.MongoClient()  #初始化本地客户端
    db = client.lagou
    collection = db.lagou
    collection.insert(data) 



def w_txt(doc):
    """
        存储到txt文本中
    """
    with open("lagou.txt",'w') as f:
        f.write(doc)
    

#主程序
def main():
    box_header = ['positionName','salary','workYear']
    #save_single_info(box_header)  #写入表头
    downloader()      #url创建，并返回提取到的信息
    #result_item = html_parse(item)  #信息解析
    #result_save(result_item)


#运行程序
if __name__ == '__main__':
    start_time = time()
    print("working...")
    main()
    end_time = time()
    print("运行结束，用时：")
    total_time = (end_time - start_time)/60
    print(total_time)