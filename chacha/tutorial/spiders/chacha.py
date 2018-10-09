# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from scrapy import Request

from tutorial.items import TutorialItem
import json
import time
import urllib
import os

class QichaSpider(scrapy.Spider):
    name = "chacha"
    allowed_domains = ["http://www.chacha.top/"]
    start_urls = ['https://www.chacha.top/origin?province_code=510000&city_code=510100&query_text=%E5%88%9B%E4%B8%9A&obj_type=1'
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

        # self.location = 'D:/pydemo/qichacha/chacha/download/' + currentDayFile + '/'
        # os.path.abspath(os.path.join(os.getcwd(), "../.."))
        self.location = os.path.abspath(os.path.join(os.getcwd(), "../.."))  + '/download/' + currentDayFile + '/'


        super(QichaSpider, self).__init__()

        dispatcher.connect(self.spider_closed,signals.spider_closed)


    def spider_closed(self,spider):   #当爬虫退出的时候 关闭chrome
        print ("chacha spider closed")

    def parse(self, response):

        startLen = self.len
        print "from parse end ---> " + str(startLen)

        searchList = response.xpath('//li[@class="list-item"]')
        if len(searchList) == 0: # 某些细则, list样式
            searchList = response.xpath('//li[@class="sup-list-item m-b-md"]')

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

                if index == 2: # 对接item项
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
        return str(url).find('announce') != -1 or str(url).find('publicity') != -1

    def isHyperPolicy(self, url):
        return str(url).find('sup_policy') != -1 or str(url).find('macro_policy') != -1 or str(url).find('imple_regu') != -1

    # 搜索 通知公示项
    # 通知 announce
    # 公示 publicity
    def parseHyperAnn(self, response):  # https://www.chacha.top/announce?id=274b53d9e06f3cc04c95
        print 'announce : ---> ' +  response.url
        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = self.getType(response.url)
            com['url'] = response.url
            com['index'] = self.map[response.url]

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            progressDiv = titleDiv.xpath('.//span[@class="policy-label"]/text()')
            if len(progressDiv) > 0:  # 某些公示性文件 没有进度
                titleLabel = progressDiv[0].extract()
                com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式
            # 适用地区 发文时间
            # 扶持金额  有效期
            # 适用行业
            for info in infos:
                for infoSpan in info.xpath('span'):
                    value = self.decodeStr(infoSpan.extract())
                    if value.find('适用地区') != -1:
                        areaSpan = infoSpan.xpath('./text()')[0].extract()
                        com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip() # 奇怪的分号
                    elif value.find('发文时间') != -1:
                        updateTime = infoSpan.xpath('.//span/text()')[0].extract()
                        com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()
                    elif value.find('扶持金额') != -1:
                        moneySpan = infoSpan.xpath('.//span//span/text()')
                        if len(moneySpan) > 0:
                            money = moneySpan[0].extract()   #金额
                            com['money'] = self.decodeStr(money).replace("扶持金额", "").replace("：","").rstrip().lstrip()
                    elif value.find('有效期限') != -1:
                        validSpan = infoSpan.xpath('./text()')
                        if len(validSpan) > 0:
                            validTime = validSpan[0].extract()
                            com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()
                    elif value.find('公示类型') != -1:
                        public = infoSpan.xpath('./text()')[0].extract()
                        com['notetype'] = self.decodeStr(public).replace("公示类型", "").replace("：","").rstrip().lstrip()
                    elif value.find('行业') != -1:
                        industry = infoSpan.xpath('.//span/text()')[0].extract()
                        com['industry'] = self.decodeStr(industry).rstrip().lstrip()
                    else:
                        pass


            #申报 内容详情
            leftContent = response.xpath('//div[@class="pull-left content-left policy-content-box bg-white m-b-md"]//div[@class="m-b-md"]')
            for left in leftContent:
                value = self.decodeStr(left.extract())
                if value.find('申报详情') != -1 or value.find('公示详情') != -1:
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
                        if fileUrl.find('http://') != -1 or fileUrl.find('https://') != -1:
                            urllib.urlretrieve(fileUrl, filename=name)
                elif value.find('政策时间轨迹') != -1:
                    pass
                else:
                    pass

            yield com

    # 搜索 扶持
    def parseHyperItem(self, response): # https://www.chacha.top/sup_item?id=aad86a5a974c55c59aaf
        print 'sup_item : ---> ' +  response.url
        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = self.getType(response.url)
            com['url'] = response.url
            com['index'] = self.map[response.url]

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            progressDiv = titleDiv.xpath('.//span[@class="policy-label"]/text()')
            if len(progressDiv) > 0:  # 某些公示性文件 没有进度
                titleLabel = progressDiv[0].extract()
                com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式

            # 适用地区 发文时间  文号
            # 政策分类 扶持金额 有效期限
            for info in infos:
                for infoSpan in info.xpath('span'):
                    value = self.decodeStr(infoSpan.extract())

                    if value.find('适用地区') != -1:
                        areaSpan = infoSpan.xpath('./text()')[0].extract()
                        com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip()
                    elif value.find('行业') != -1:
                        industry = infoSpan.xpath('.//span/text()')[0].extract()  #行业
                        com['industry'] = self.decodeStr(industry).rstrip().lstrip()
                    elif value.find('有效期限') != -1:
                        validSpan = infoSpan.xpath('.//span/text()')
                        if len(validSpan) > 0:
                            validTime = validSpan[0].extract()
                            com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()
                    elif value.find('扶持金额') != -1:
                        moneySpan = infoSpan.xpath('.//span//span/text()')
                        if len(moneySpan) > 0:
                            money = moneySpan[0].extract()   #金额
                            com['money'] = self.decodeStr(money).replace("扶持金额", "").replace("：","").rstrip().lstrip()
                    elif value.find('发文时间') != -1:
                        updateSpan = infoSpan.xpath('./text()')
                        if len(updateSpan) > 0:
                            updateTime = updateSpan[0].extract()
                            com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()
                    elif value.find('政策分类') != -1:
                        types = ''
                        for type in infoSpan.xpath('span'):
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
                        if fileUrl.find('http://') != -1 or fileUrl.find('https://') != -1:
                            urllib.urlretrieve(fileUrl, filename=name)
                elif value.find('政策时间轨迹') != -1:
                    pass
                else:
                    pass

            yield com


    # 搜索 文件   相关政府政策文件 需要登录获取文件
    # 指导性文件 macro_policy
    # 扶持政策 sup_policy
    # 实施细则 imple_regu
    def parseHyperPolicy(self, response): # https://www.chacha.top/sup_policy?id=d0c7431587332fef3a27
        print 'sup_policy : ---> ' +  response.url

        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = self.getType(response.url)
            com['url'] = response.url
            com['index'] = self.map[response.url]

            topDiv = response.xpath('//div[@class="policy-item-top m-t-md m-b-md"]')

            titleDiv = topDiv.xpath('.//div[@class="policy-title pull-left"]')
            title = titleDiv.xpath('.//span[@class="bold font-24"]/text()')[0].extract()
            com['title'] = self.decodeStr(title)

            progressDiv = titleDiv.xpath('.//span[@class="policy-label"]/text()')
            if len(progressDiv) > 0:  # 某些公示性文件 没有进度
                titleLabel = progressDiv[0].extract()
                com['progress'] = self.decodeStr(titleLabel)

            infos = topDiv.xpath('p')   # 直接按照固定格式

            # 适用地区 发文时间 文号
            # 发文体系 有效时间
            for info in infos:
                for infoSpan in info.xpath('span'):
                    value = self.decodeStr(infoSpan.extract())
                    if value.find('适用地区') != -1:
                        areaSpan = infoSpan.xpath('./text()')[0].extract()
                        com['area'] = self.decodeStr(areaSpan).replace("适用地区", "").replace("：","").rstrip().lstrip()
                    elif value.find('发文时间') != -1:
                        updateTime = infoSpan.xpath('./text()')[0].extract()
                        com['updateTime'] = self.decodeStr(updateTime).replace("发文时间", "").replace("：","").rstrip().lstrip()
                    elif value.find('文号') != -1:
                        number = infoSpan.xpath('./text()')[0].extract()
                        com['number'] = self.decodeStr(number).replace("文号", "").replace("：","").rstrip().lstrip()
                    elif value.find('发文体系') != -1:
                        system = infoSpan.xpath('.//span/text()')
                        if len(system) > 0:
                            money = system[0].extract()
                            com['system'] = self.decodeStr(money).replace("发文体系", "").replace("：","").rstrip().lstrip()
                    elif value.find('有效期限') != -1:
                        validSpan = infoSpan.xpath('./text()')
                        if len(validSpan) > 0:
                            validTime = validSpan[0].extract()
                            com['validTime'] = self.decodeStr(validTime).replace("有效期限", "").replace("：","").rstrip().lstrip()
                    else:
                        pass

            # 政策原文
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
                            if fileUrl.find('http://') != -1 or fileUrl.find('https://') != -1:
                                urllib.urlretrieve(fileUrl, filename=name)
                elif value.find('政策时间轨迹') != -1:
                    pass
                else:
                    pass

            yield com


    def getType(self, url):
        if url.find('sup_policy'): #文件  扶持
            return 'sup_policy'
        elif url.find('macro_policy'):# 文件  指导性文件
            return 'macro_policy'
        elif url.find('imple_regu'): #文件  实施细则
            return 'imple_regu'

        elif url.find('announce'): # 通知 通知
            return 'announce'
        elif url.find('publicity'): # 通知 公示
            return 'publicity'

        elif url.find('sup_item'):  # 扶持
            return 'sup_item'

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
        com['notetype'] = ''

        return com

    def decodeStr(self, value):
        return json.dumps(value).decode('unicode_escape')







