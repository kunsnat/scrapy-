# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from scrapy import Request

from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.http import HtmlResponse
from tutorial.items import TutorialItem
import urlparse
import json
import time
import urllib
from openpyxl import Workbook

class QichaSpider(scrapy.Spider):
    name = "chacha"
    allowed_domains = ["http://www.chacha.top/"]
    start_urls = ['https://www.chacha.top/search?province_code=510000&city_code=510100&query_text=%E5%88%9B%E4%B8%9A'
                  ]

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        self.browser.implicitly_wait(10)
        self.len = 0

        self.hyperBrowser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        self.hyperBrowser.implicitly_wait(10)

        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['标题', '进度', '类型', '适用地区', '发文时间', '扶持金额', '有效期限', '适用行业', '政策分类', '申报详情', '附件列表'])  # 设置表头

        super(QichaSpider, self).__init__()

        dispatcher.connect(self.spider_closed,signals.spider_closed)


    def spider_closed(self,spider):   #当爬虫退出的时候 关闭chrome
        print ("spider closed")

    # def parse_start_url(self, response):
    #     com = TutorialItem()
    #     # yield com
    #
    #     yield Request(self.start_urls[0], callback=self.parse)

    def parse(self, response):

        startLen = self.len
        print "from parse end ---> " + str(startLen)

        searchList = response.xpath('//li[@class="list-item"]')

        if response.url == self.start_urls[0]:
            self.len = len(searchList)

            for index, items in enumerate(searchList):
                hyper = items.xpath('.//a/@href')[0].extract()
                hyperUrl = 'https://www.chacha.top' + hyper

                if self.isHyperAnn(hyperUrl):
                    yield Request(url=hyperUrl,callback=self.parseHyperAnn, dont_filter=True)
                else:
                    yield Request(url=hyperUrl,callback=self.parseHyperItem, dont_filter=True)

                break
                # time.sleep(2) # 保留加载时间消耗.


        if self.len > startLen: # 继续迭代爬取数据
            pass
            # yield Request(url='http://www.baidu.com',callback=self.parse, dont_filter=True)
            # yield Request(url=self.start_urls[0],callback=self.parse, dont_filter=True)

        else:
            if self.isHyperlink(response.url):
                print 'parse from url hyper' # 超链 需要的单独管道下载数据.
            print 'list is end no more '


    def isHyperlink(self, url):
        return self.isHyperAnn(url) or self.isHyperItem(url)

    def isHyperItem(self, url):
        return str(url).find('sup_item') != -1 or str(url).find('baidu') != -1

    def isHyperAnn(self, url):
        return str(url).find('announce') != -1


    def parseHyperAnn(self, response):  # https://www.chacha.top/announce?id=274b53d9e06f3cc04c95
        print 'parse hyper announce: ---> ' +  response.url
        if response.url != self.start_urls[0]:
            com = TutorialItem()
            com['type'] = 'announce'
            com['url'] = response.url
            com['policyType'] = ''

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            titleLabel = titleDiv.xpath('.//span[@class="policy-label"]/text()')[0].extract()
            com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式

            # 适用地区 发文时间
            areaSpan = infos[0].xpath('.//span')[0].xpath('./text()')[0].extract()
            com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip() # 奇怪的分号

            updateTime = infos[0].xpath('.//span')[1].xpath('.//span/text()')[0].extract()
            com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()

            # 扶持金额  有效期
            money = infos[1].xpath('.//span//span//span/text()')[0].extract()
            com['money'] = self.decodeStr(money).replace("扶持金额", "").replace("：","").rstrip().lstrip()

            validTime = infos[1].xpath('span')[1].xpath('./text()')[0].extract()
            com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()

            #适用行业
            industry = infos[2].xpath('.//span//span/text()')[0].extract()
            com['industry'] = self.decodeStr(industry).rstrip().lstrip()

            #内容详情
            leftContent = response.xpath('//div[@class="pull-left content-left policy-content-box bg-white m-b-md"]//div[@class="m-b-md"]')

            #申报
            content = leftContent[0].xpath('.//div[@class="detail-content"]').extract()
            # com['content'] = self.decodeStr(content).rstrip().lstrip()

            #时间轨迹leftContent[1]
            #附件leftContent[2]

            urls = leftContent[2].xpath('.//li[@class="ev-download m-b-sm"]')
            urlList = []
            for url in urls:
                fileUrl = 'http:' + str(url.xpath('@data-href')[0].extract())
                name = url.xpath('.//a/text()')[0].extract()
                if fileUrl.find('.pdf') != -1:
                    urllib.urlretrieve(fileUrl, filename=name)
                else:
                    urlList.append(fileUrl)
                # break

            com['file_urls'] = urlList
            # com['file_urls'] = ['http://cdn.chacha.top/upload/announcement/201809/2018年成都市新经济梯度培育企业申报书.docx']

            yield com

    def parseHyperItem(self, response):
        print 'parse hyper: ---> ' +  response.url

        if response.url != self.start_urls[0]:
            com = TutorialItem()
            com['type'] = 'sup_item'
            com['url'] = response.url
            com['policyType'] = ''

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            titleLabel = titleDiv.xpath('.//span[@class="policy-label"]/text()')[0].extract()
            com['progress'] = self.decodeStr(titleLabel)

            # 适用地区 适用行业 有效期限 发文时间

            infos = topDiv.xpath('.//p')
            for info in infos:
                values = info.xpath('.//span')
                for value in values:
                    test = value.xpath('./text()')

            yield com


    def decodeStr(self, value):
        return json.dumps(value).decode('unicode_escape')







