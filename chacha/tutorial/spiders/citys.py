# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals

from selenium import webdriver
from pydispatch import dispatcher

import json

from openpyxl import Workbook
import os
import time
import xlrd
import xlwt

from chacha.tutorial.items import CityItem


class CitySpider(scrapy.Spider):
    name = "citys"
    allowed_domains = ["http://www.chacha.top/"]
    start_urls = [
            'https://www.chacha.top/search?query_text=%E5%88%9B%E4%B8%9A&area=true',  # 获取省份
            'https://www.chacha.top/search?province_code=510000',  #获取对应城市
            'https://www.chacha.top/search?province_code=510000&city_code=510100',  #获取对应区县
                  ]

    # province_code 省份
    # city_code 城市
    # district_code 区县

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        self.browser.implicitly_wait(10)

        self.workBookMap = {}

        self.location = 'D:/pydemo/qichacha/chacha/download/areacode/'

        if os.path.exists(self.location):
            pass
        else:
            os.makedirs(self.location)

        super(CitySpider, self).__init__()

        dispatcher.connect(self.spider_closed,signals.spider_closed)


    def spider_closed(self, spider):
        print (" --->" + spider.name + " spider closed")

    def parse(self, response):
        print (" --->" + self.name + " parse")

        if response.url.find('city_code') != -1:  # 路径精确到了城市, 遍历对应区县
            districts = response.xpath('.//div[@id="_citys2"]')
            for district in districts.xpath('a'):
                com = self.initItem()
                com['url'] = response.url
                com['id'] = district.xpath('@data-id')[0].extract()
                com['name'] = district.xpath('@data-name')[0].extract()
                com['title'] = district.xpath('@title')[0].extract()
                com['text'] = district.xpath('text()')[0].extract()
                com['level'] = district.xpath('@data-level')[0].extract()
                yield com
        elif response.url.find('province_code') != -1:# 路径精确到了省份, 遍历对应城市
            citys = response.xpath('.//div[@id="_citys1"]')
            for city in citys.xpath('a'):
                com = self.initItem()
                com['url'] = response.url
                com['id'] = city.xpath('@data-id')[0].extract()
                com['name'] = city.xpath('@data-name')[0].extract()
                com['title'] = city.xpath('@title')[0].extract()
                com['text'] = city.xpath('text()')[0].extract()
                com['level'] = city.xpath('@data-level')[0].extract()
                yield com

        else:
            provinces = response.xpath('.//div[@id="_citys0"]')
            for province in provinces.xpath('a'):
                com = self.initItem()
                com['url'] = response.url
                com['id'] = province.xpath('@data-id')[0].extract()
                com['name'] = province.xpath('@data-name')[0].extract()
                com['text'] = province.xpath('text()')[0].extract()
                com['level'] = province.xpath('@data-level')[0].extract()
                yield com

    def initItem(self):
        com = CityItem()
        com['title'] = ''
        com['name'] = ''
        com['text'] = ''
        com['id'] = ''
        com['level'] = ''

        return com

    def decodeStr(self, value):
        return json.dumps(value).decode('unicode_escape')