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
import os
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
        self.map = {}
        self.needLogin = True

        currentDayFile = time.strftime("%Y-%m-%d", time.localtime())

        self.location = 'D:/pydemo/qichacha/chacha/download/' + currentDayFile + '/'


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

                if index < startLen:
                    continue

                hyper = items.xpath('.//a/@href')[0].extract()
                hyperUrl = 'https://www.chacha.top' + hyper

                self.map[hyperUrl] = index
                self.index = index

                print 'current index ---------->  ' + str(index)

                if self.isHyperAnn(hyperUrl):
                    yield Request(url=hyperUrl,callback=self.parseHyperAnn, dont_filter=True)
                elif self.isHyperPolicy(hyperUrl):
                    yield Request(url=hyperUrl,callback=self.parseHyperPolicy, dont_filter=True)
                else:
                    yield Request(url=hyperUrl,callback=self.parseHyperItem, dont_filter=True)

                if index == 4: # 对接item项
                    break

        if self.len > startLen: # 继续迭代爬取数据
            pass
            # yield Request(url='http://www.baidu.com',callback=self.parse, dont_filter=True)
            # yield Request(url=self.start_urls[0],callback=self.parse, dont_filter=True)

        else:
            if self.isHyperlink(response.url):
                print 'parse from url hyper' # 超链 需要的单独管道下载数据.
            print 'list is end no more '


    def isHyperlink(self, url):
        return self.isHyperAnn(url) or self.isHyperItem(url) or self.isHyperPolicy(url)

    def isHyperItem(self, url):
        return str(url).find('sup_item') != -1 or str(url).find('baidu') != -1

    def isHyperAnn(self, url):
        return str(url).find('announce') != -1

    def isHyperPolicy(self, url):
        return str(url).find('sup_policy') != -1


    #通知公式
    def parseHyperAnn(self, response):  # https://www.chacha.top/announce?id=274b53d9e06f3cc04c95
        print 'parse hyper announce: ---> ' +  response.url
        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = 'announce'
            com['url'] = response.url
            com['index'] = self.map[response.url]

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            titleLabel = titleDiv.xpath('.//span[@class="policy-label"]/text()')[0].extract()
            com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式

            # 适用地区 发文时间
            firsts = infos[0].xpath('span')
            for firstSpan in firsts:
                value = self.decodeStr(firstSpan.extract())
                if value.find('适用地区') != -1:
                    areaSpan = firstSpan.xpath('./text()')[0].extract()
                    com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip() # 奇怪的分号
                elif value.find('发文时间') != -1:
                    updateTime = firstSpan.xpath('.//span/text()')[0].extract()
                    com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()
                else:
                    pass

            # 扶持金额  有效期
            seconds = infos[1].xpath('span')
            for secondSpan in seconds:
                value = self.decodeStr(secondSpan.extract())
                if value.find('扶持金额') != -1:
                    moneySpan = secondSpan.xpath('.//span//span/text()')
                    if len(moneySpan) > 0:
                        money = moneySpan[0].extract()   #金额
                        com['money'] = self.decodeStr(money).replace("扶持金额", "").replace("：","").rstrip().lstrip()
                elif value.find('有效期限') != -1:
                    validSpan = secondSpan.xpath('./text()')
                    if len(validSpan) > 0:
                        validTime = validSpan[0].extract()
                        com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()
                else:
                    pass


            #适用行业
            industry = infos[2].xpath('.//span//span/text()')[0].extract()
            com['industry'] = self.decodeStr(industry).rstrip().lstrip()

            #申报 内容详情
            leftContent = response.xpath('//div[@class="pull-left content-left policy-content-box bg-white m-b-md"]//div[@class="m-b-md"]')
            for left in leftContent:
                value = self.decodeStr(left.extract())
                if value.find('申报详情') != -1:
                    content = left.xpath('.//div[@class="detail-content"]').extract()
                    com['content'] = self.decodeStr(content).rstrip().lstrip()
                elif value.find('资料下载') != -1:
                    location = self.location + 'files/' + title + '/' # 附件对应地址
                    if os.path.exists(location):
                        pass
                    else:
                        os.makedirs(location)

                    urls = left.xpath('.//li[@class="ev-download m-b-sm"]')
                    for url in urls:
                        fileUrl = 'http:' + str(url.xpath('@data-href')[0].extract())
                        name = location + url.xpath('.//a/text()')[0].extract()
                        urllib.urlretrieve(fileUrl, filename=name)
                elif value.find('政策时间轨迹') != -1:
                    pass
                else:
                    pass

            yield com

    #扶持条款
    def parseHyperItem(self, response): # https://www.chacha.top/sup_item?id=aad86a5a974c55c59aaf
        print 'parse hyper sup_item : ---> ' +  response.url
        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = 'sup_item'
            com['url'] = response.url
            com['index'] = self.map[response.url]

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            titleLabel = titleDiv.xpath('.//span[@class="policy-label"]/text()')[0].extract()
            com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式

            # ---------> 适用地区 发文时间  文号

            areaSpan = infos[0].xpath('.//span')[0].xpath('./text()')[0].extract()
            com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip() # 奇怪的分号

            industry = infos[0].xpath('.//span//span/text()')[0].extract()  #行业
            com['industry'] = self.decodeStr(industry).rstrip().lstrip()

            validSpan = infos[0].xpath('span')[2].xpath('.//span/text()')
            if len(validSpan) > 0:
                validTime = validSpan[0].extract()
                com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()

            # ------>  政策分类 扶持金额 发文时间
            seconds = infos[1].xpath('span')
            for secondSpan in seconds:
                value = self.decodeStr(secondSpan.extract())
                if value.find('扶持金额') != -1:
                    moneySpan = secondSpan.xpath('.//span//span/text()')
                    if len(moneySpan) > 0:
                        money = moneySpan[0].extract()   #金额
                        com['money'] = self.decodeStr(money).replace("扶持金额", "").replace("：","").rstrip().lstrip()
                elif value.find('发文时间') != -1:
                    updateSpan = secondSpan.xpath('./text()')
                    if len(updateSpan) > 0:
                        updateTime = updateSpan[0].extract()
                        com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()
                elif value.find('政策分类') != -1:
                    types = ''
                    for type in secondSpan.xpath('span'):
                        value = type.xpath('./text()')[0].extract()
                        if types == '':
                            types += str(self.decodeStr(value))
                        else:
                            types += ',' + str(self.decodeStr(value))

                    com['policyType'] = types
                else:
                    pass

            #申报 扶持详情
            leftContent = response.xpath('//div[@class="pull-left content-left policy-content-box bg-white m-b-md"]//div[@class="m-b-md"]')
            for left in leftContent:
                value = self.decodeStr(left.extract())
                if value.find('申报详情') != -1 or value.find('扶持详情') != -1:
                    content = left.xpath('.//div[@class="detail-content"]').extract()
                    com['content'] = self.decodeStr(content).rstrip().lstrip()
                elif value.find('资料下载') != -1:
                    location = self.location + 'files/' + title + '/' # 附件对应地址
                    if os.path.exists(location):
                        pass
                    else:
                        os.makedirs(location)

                    urls = left.xpath('.//li[@class="ev-download m-b-sm"]')
                    for url in urls:
                        fileUrl = 'http:' + str(url.xpath('@data-href')[0].extract())
                        name = location + url.xpath('.//a/text()')[0].extract()
                        urllib.urlretrieve(fileUrl, filename=name)
                elif value.find('政策时间轨迹') != -1:
                    pass
                else:
                    pass

            yield com


    # 政策原文   需要登录获取文件
    def parseHyperPolicy(self, response): # https://www.chacha.top/sup_policy?id=d0c7431587332fef3a27
        print 'parse hyper sup_policy : ---> ' +  response.url

        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = 'sup_policy'
            com['url'] = response.url
            com['index'] = self.map[response.url]

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            titleLabel = titleDiv.xpath('.//span[@class="policy-label"]/text()')[0].extract()
            com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式

            # ---------> 适用地区 发文时间 文号
            # 适用地区 发文时间
            firsts = infos[0].xpath('span')
            for firstSpan in firsts:
                value = self.decodeStr(firstSpan.extract())
                if value.find('适用地区') != -1:
                    areaSpan = firstSpan.xpath('./text()')[0].extract()
                    com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip() # 奇怪的分号
                elif value.find('发文时间') != -1:
                    updateTime = firstSpan.xpath('./text()')[0].extract()
                    com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()
                elif value.find('文号') != -1:
                    number = firstSpan.xpath('./text()')[0].extract()
                    com['number'] = self.decodeStr(number).replace("文号", "").replace("：","").rstrip().lstrip()
                else:
                    pass


            seconds = infos[1].xpath('span')
            for secondSpan in seconds:
                value = self.decodeStr(secondSpan.extract())
                if value.find('发文体系') != -1:
                    system = secondSpan.xpath('.//span/text()')
                    if len(system) > 0:
                        money = system[0].extract()
                        com['system'] = self.decodeStr(money).replace("发文体系", "").replace("：","").rstrip().lstrip()
                elif value.find('有效期限') != -1:
                    validSpan = secondSpan.xpath('./text()')
                    if len(validSpan) > 0:
                        validTime = validSpan[0].extract()
                        com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()
                else:
                    pass

            # ------>  政策原文

            leftContent = response.xpath('//div[@class="pull-left content-left bg-white m-b-md"]//div[@class="m-b-md"]') #特殊的class
            for left in leftContent:
                value = self.decodeStr(left.extract())
                if value.find('政策原文') != -1:
                    content = left.xpath('.//div[@class="detail-content"]').extract()
                    com['content'] = self.decodeStr(content).rstrip().lstrip()
                elif value.find('资料下载') != -1:
                    location = self.location + 'files/' + title + '/' # 附件对应地址
                    if os.path.exists(location):
                        pass
                    else:
                        os.makedirs(location)

                    urls = left.xpath('.//li[@class="m-b-sm"]')   #特殊的li
                    for url in urls:
                        value = url.xpath('.//a').xpath('@href')
                        if len(value) > 0:
                            fileUrl = 'http:' + str(value[0].extract())
                            name = location + url.xpath('.//a/text()')[0].extract()
                            urllib.urlretrieve(fileUrl, filename=name)
                elif value.find('政策时间轨迹') != -1:
                    pass
                else:
                    pass

            yield com


            # 需要补充 公式样式节点.  1234567890

    def initItem(self):
        com = TutorialItem()
        com['title'] = ''
        com['progress'] = ''
        com['type'] = ''
        com['area'] = ''
        com['updateTime'] = ''
        com['money'] = ''
        com['validTime'] = ''
        com['industry'] = ''
        com['url'] = ''
        com['policyType'] = ''
        com['content'] = ''
        com['index'] = ''
        com['number'] = ''
        com['system'] = ''

        return com

    def decodeStr(self, value):
        return json.dumps(value).decode('unicode_escape')







