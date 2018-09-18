# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from item import Test
from qichacha.items import DemoItem


class QichaSpider(scrapy.Spider):
    name = "qicha"
    allowed_domains = ["http://www.qichacha.com/"]
    start_urls = ['http://www.qichacha.com/',
                  'https://www.qichacha.com/search?key=四川科技',
                  # 'https://www.qichacha.com/search?key=%E5%9B%9B%E5%B7%9D%E7%A7%91%E6%8A%80'
                  ]

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        super(QichaSpider, self).__init__()


        dispatcher.connect(self.spider_closed,signals.spider_closed)


    def spider_closed(self,spider):
        #当爬虫退出的时候 关闭chrome
        print ("spider closed")
        # self.browser.quit()

    def parse(self, response):
          print "from parse end ---> "
          com = DemoItem()
          yield com

