# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy import Request

from selenium import webdriver
from pydispatch import dispatcher

from tutorial.items import CheckItem
import json


class CheckSpider(scrapy.Spider):
    name = "check"
    allowed_domains = ["http://www.chacha.top/"]
    start_urls = ['https://www.chacha.top/origin?province_code=510000&city_code=510100&query_text=%E5%88%9B%E4%B8%9A&obj_type=1'
                  ]

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        self.browser.implicitly_wait(10)

        super(CheckSpider, self).__init__()

        dispatcher.connect(self.spider_closed,signals.spider_closed)


    def spider_closed(self, spider):   #当爬虫退出的时候 关闭chrome
        print ("check spider closed")

    def parse(self, response):
        print "check parse end  ---> "

        searchList = response.xpath('//li[@class="list-item"]')
        if len(searchList) == 0: # 某些细则, list样式
            searchList = response.xpath('//li[@class="sup-list-item m-b-md"]')

        if response.url == self.start_urls[0]:
            for index, items in enumerate(searchList):
                hyper = items.xpath('.//a/@href')[0].extract()
                hyperUrl = 'https://www.chacha.top' + hyper

                print 'current index ---------->  ' + str(index)

                com = CheckItem()
                com['test'] = 111

                yield Request(url=hyperUrl,callback=self.parseHyper, dont_filter=True)

                break
        else:
            print 'list is end no more '


    # 检测超链 hyper 提取标题 判断和数据库的比对 是否需要更新
    def parseHyper(self, response):  # https://www.chacha.top/announce?id=274b53d9e06f3cc04c95
        print 'announce : ---> ' +  response.url
        if response.url != self.start_urls[0]:
            com = self.initItem()

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['test'] = self.decodeStr(title)

            yield com

    def initItem(self):
        com = CheckItem()
        com['test'] = ''

        return com

    def decodeStr(self, value):
        return json.dumps(value).decode('unicode_escape')