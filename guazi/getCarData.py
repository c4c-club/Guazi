# -*- coding: utf-8 -*-
# @Time : 2020/7/22 15:57
# @Author : C4C
# @File : getCarData.py
# @Remark : 瓜子二手车爬虫

import os
import time
import requests as rq
from bs4 import BeautifulSoup as bs
import csv
import re
import random

#请求城市页面获取车辆url
def getCarUrl(city_url,car_url):
    #https://www.guazi.com/bj/buy/o5
    count = 0
    count_all = 0
    base_url = 'https://www.guazi.com'
    for city in city_url:
        print('正在获取：'+city)
        for index in range(1,51):
            print('正在获取'+city+'第：'+str(index)+' 页')
            url = 'https://www.guazi.com/'+city+'/buy/o'+ str(index)
            respones = rq.get(url=url,headers=header,timeout=3)
            #print(respones.status_code)
            if respones.status_code == 200:
                respones.encoding = 'utf=8'
                city_html = respones.text
                soup = bs(city_html,'lxml')#返回网页
                car_ul = soup.select_one('.carlist')#ul
                car = car_ul.select('a')
                for c in car:
                    #print(c.get('href'))
                    car_url.append(base_url+c.get('href'))
                    #每个城市获取条目计数
                    count += 1
        count_all += count
        print(city+'共获取：'+str(count)+'条')
        count = 0
    print('\n所有城市共获取：'+str(count_all)+'条')


    file = open('car_url.csv','w',newline='',encoding='utf-8')
    csvwirter = csv.writer(file)
    for item in car_url:
        csvwirter.writerow([item])


#去除重复链接
def removeDuplicates(car_url):
    real_car_url = []
    for i in car_url:
        if i not in real_car_url:
            real_car_url.append(i)
    print('\n去重后：'+str(len(real_car_url)))
    return real_car_url

#请求车辆页面获取数据
def getCarDetail(real_car_url):
    count = 0
    count10 = 0
    car_info_list = []
    print('\n获取信息ing...')


    for url in real_car_url:
        #防止网站反爬拒绝访问导致整个程序崩溃
        try:
            respones = rq.get(url=url,headers=header,timeout=5)
            if respones.status_code == 200:
                respones.encoding = 'utf=8'
                car_html = respones.text
                soup = bs(car_html, 'lxml')  # 返回car页面

                #获取城市
                city = soup.select_one('title').text[0:2]

                #获取标题
                title = soup.select_one('.titlebox').text
                searchObj1 = re.search(r'([\u4e00-\u9fa5]+.).+', title, re.I)
                if searchObj1:
                    real_title = searchObj1.group().replace('\r','')
                else:
                    real_title = 'null'

                #品牌
                brand = real_title.split(' ',1)[0]
                #年份
                searchObj2 = re.search(r'\d\d\d\d', real_title, re.I)
                if searchObj2:
                    year = searchObj2.group()
                else:
                    year = '未知年份'

                #车辆信息
                info = soup.select('ul.assort span')
                #已开里程（万公里）
                length = info[1].text[:-3]
                #排量
                power = info[2].text
                #变速箱
                gearbox = info[3].text

                #价格
                pris = soup.select('div.price-main span')
                price = pris[0].text[:-1]


                car = {
                    '城市':city,
                    '年份':year,
                    '品牌':brand,
                    '名称': real_title,
                    '价格': price,#（万元）
                    '已开里程': length,#（万公里）
                    '排量': power,
                    '变速箱': gearbox,
                }
        except:
            time.sleep(30)#防反爬休眠
            print('无效页面')

        #讲字典加入汽车信息(car_info_list)列表
        car_info_list.append(car)
        #计数+1
        count +=1;
        #整10输出，并清零计数，并休眠两秒（防反爬）
        if (count%10)==0:
            count10 +=count
            print('已获取：'+str(count10)+'条')
            time.sleep(0.2)
            count = 0

    print('\n已获取：'+str(len(car_info_list))+' 条')
    return car_info_list




#储存数据
def save_csv(car_info_list):
    print('\n写入ing...')
    file = open('车辆信息.csv','w',newline='',encoding='utf-8')
    csvWriter = csv.writer(file)
    for item in car_info_list:
        # 按行写入
        csvWriter.writerow([item['城市'],item['年份'],item['品牌'],item['名称'], item['价格'], item['已开里程'], item['排量'], item['变速箱']])
    file.close()




if __name__ == '__main__':
    #定义随机header
    header1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'Cookie': 'antipas=3K603qk13O111982990078362;cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22seo_baidu%22%2C%22ca_n%22%3A%22default%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22%25e7%2593%259c%25e5%25ad%2590%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%228edc615a-76bd-44d0-8853-85870ece6a35%22%2C%22ca_city%22%3A%22ezhou%22%2C%22sessionid%22%3A%22c0cc9e05-f3d5-4024-eeaa-adc8aa2f8980%22%7D;sessionid=c0cc9e05-f3d5-4024-eeaa-adc8aa2f8980'
    }
    header2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Cookie':'antipas=U799868808859159I332S1652;cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22seo_baidu%22%2C%22ca_n%22%3A%22default%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22a22198f7-1a0d-4505-d0f3-d86775b22794%22%2C%22ca_city%22%3A%22ezhou%22%2C%22sessionid%22%3A%22fa741e99-fe17-43d1-f935-06ac0757b197%22%7D;sessionid=fa741e99-fe17-43d1-f935-06ac0757b197'
    }
    header3 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40',
        'Cookie': 'antipas=04502p7A870278947H951940X57;cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22seo_baidu%22%2C%22ca_n%22%3A%22default%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22efde8975-bd5e-4f39-8260-1777903fa835%22%2C%22ca_city%22%3A%22ezhou%22%2C%22sessionid%22%3A%22a5c0fb51-cf45-462e-dac6-840810fde034%22%7D;sessionid=a5c0fb51-cf45-462e-dac6-840810fde034'
    }
    header4 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Cookie': 'antipas=n29R32226624595527Se611919Gd8;cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22self%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%220ed0b615-9420-4bc6-c8b6-020241680b45%22%2C%22ca_city%22%3A%22ezhou%22%2C%22sessionid%22%3A%22ea2c4b28-e286-4bba-f38b-41cff34a0310%22%7D;sessionid=ea2c4b28-e286-4bba-f38b-41cff34a0310'
    }
    headList = [header1, header2,header3,header4]
    headerindex = random.randrange(0, len(headList))
    header = headList[headerindex]

    #每个城市的url
    #北京 上海 广州 深圳 成都 重庆 杭州 苏州 沈阳 武汉
    city_url = ['bj','sh','gz','sz','cd','cq','hz','su','sy','wh']
    #city_url = ['bj','sh','gz','sz','cd']
    #city_url = ['bj']
    #车辆页面的url
    car_url = []

    getCarUrl(city_url, car_url)
    #去重后的车的url
    real_car_url = removeDuplicates(car_url)
    #获取到的车辆信息
    car_info_list = getCarDetail(real_car_url)
    #储存
    save_csv(car_info_list)




