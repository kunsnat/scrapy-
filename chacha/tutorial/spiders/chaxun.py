# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from scrapy.cmdline import execute
import sys
import os

from scrapy import Request

import json
import urllib

from openpyxl import Workbook
import xlrd
import xlwt
import os
import time

import logging

from chacha.tutorial.items import ChaXunItem


class QichaSpider(scrapy.Spider):
    name = "chaxun"
    allowed_domains = ["http://www.chacha.top/"]
    start_urls = [
                'https://www.chacha.top/sup?province_code=510000&city_code=510100', # 扶持
                'https://www.chacha.top/notice?province_code=510000&city_code=510100&obj_type=7', #  公示
                'https://www.chacha.top/notice?province_code=510000&city_code=510100&obj_type=4',  # 申报'
                'https://www.chacha.top/origin?province_code=510000&city_code=510100&obj_type=1', # 指导性文件'
                'https://www.chacha.top/origin?province_code=510000&city_code=510100&obj_type=2', # 扶持政策'
                'https://www.chacha.top/origin?province_code=510000&city_code=510100&obj_type=3' # 实施细则'
                ]

    def __init__(self, index=None, *args, **kwargs):
        self.browser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        self.browser.implicitly_wait(10)
        self.len = {}
        self.index = int(index)

        self.hyperBrowser = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe")
        self.hyperBrowser.implicitly_wait(10)
        self.workBookMap = {}
        self.startUrlIndex = {}
        self.hyperIndexMap = {}
        self.fromUrl = {} # 标记最终的item, 来自哪个查询url, 便于分别保存请求.
        self.needLogin = True

        currentDayFile = time.strftime("%Y-%m-%d", time.localtime())
        self.location = 'D:/pydemo/qichacha/chacha/download/' + currentDayFile + '/'
        if os.path.exists(self.location):
            pass
        else:
            os.makedirs(self.location)

        self.areacode = 'D:/pydemo/qichacha/chacha/download/areacode/'

        # os.path.abspath(os.path.join(os.getcwd(), "../.."))
        # self.location = os.path.abspath(os.path.join(os.getcwd(), "../.."))  + '/download/' + currentDayFile + '/'

        super(QichaSpider, self).__init__()

        dispatcher.connect(self.spider_closed, signals.spider_closed)


    def getSaveName(self, discode):
        name = self.codeName[discode]
        if self.index == 0:
            name += "_扶持"
        elif self.index == 1:
            name += "公示"
        elif self.index == 2:
            name += "_申报"
        elif self.index == 3:
            name += "_指导性文件"
        elif self.index == 4:
            name += "_扶持政策"
        elif self.index == 5:
            name += "_实施细则"

        name +=  '.xlsx'
        return name

    def start_requests(self):  # 循环搜索  创建多个地址 以供查询 优先start_urls 两者选一
        urls = []

        cityCode = self.initCodeName()  # 需要遍历的区县 数组


        targetUrl = self.start_urls[self.index]
        for index, code in enumerate(cityCode):
            if index == 0:
                continue
            value = targetUrl + '&district_code=' + code
            self.len[value] = 0

            self.saveName = self.getSaveName(code)

            wb = Workbook()
            ws = wb.active
            ws.append(['标题', '发文体系', '文号', '序号',
                       '公示类型', '进度', '类型', '适用地区',
                       '发文时间', '扶持金额', '有效期限', '适用行业',
                       '政策分类', '详情', '政策轨迹', '文章地址',
                       '数据来源'
                       ])  # 设置表头
            books = {'wb':'', 'ws':''}
            books['wb'] = wb
            books['ws'] = ws
            self.startUrlIndex[value] = index
            self.workBookMap[value] = books

            urls.append(value)
            if index == 1:
                break

        for url in urls:
            yield self.make_requests_from_url(url)

    def initCodeName(self):
        # 读取excel 对应district_code区域文件, 拿到相应的code和地址, 然后保存成对应的ws
        # 根据510000 四川, 拿到对四川的 城市,   比如拿到 成都 510100  后续 对应excel 成都区域, 再添加相应的 dis区域编码
        cityExcel = self.areacode + '510100.xlsx'
        provinceExcel = self.areacode + '510000.xlsx'

        # 打开文件
        city = xlrd.open_workbook(cityExcel)
        province = xlrd.open_workbook(provinceExcel)

        # 根据sheet索引或者名称获取sheet内容
        citySheet = city.sheet_by_index(0) # sheet索引从0开始
        provinceSheet = province.sheet_by_index(0)

        # 获取整行和整列的值（数组）
        codeName = {}

        cityName= citySheet.col_values(1)
        cityCode = citySheet.col_values(4)

        provinceName = provinceSheet.col_values(1)
        provinceCode = citySheet.col_values(4)
        for index, name in enumerate(provinceName):
            if index == 0:
                continue
            code = provinceCode[index]
            codeName[code] = name

        for index, name in enumerate(cityName):
            if index == 0:
                continue
            code = cityCode[index]
            codeName[code] = name

        self.codeName = codeName

        return cityCode



    def parse(self, response):
        startLen = self.len[response.url]

        logging.info('parse start  len ----> ' + str(startLen))

        searchList = response.xpath('//li[@class="list-item"]')
        if len(searchList) == 0: # 某些细则, list样式
            searchList = response.xpath('//li[@class="sup-list-item m-b-md"]')

        self.len[response.url] = len(searchList)
        noEnd = True
        for index, items in enumerate(searchList):

            if index < startLen:
                continue

            if index % 100 == 0: # 对接item项  检测是否已经在数据库存储 --> TODO
                logging.info(" to do check need refresh data ----> ")

            progressSpan = items.xpath('.//span[@class="policy-label m-l-sm"]')
            if len(progressSpan) == 0: # 某些细则, list样式
                progressSpan = items.xpath('.//span[@class="policy-label"]')
            for progress in progressSpan:  #
                value = self.decodeStr(progress.extract())
                if value.find('申报已截止') != -1:
                    noEnd = False

            if noEnd == False:
                logging.info(" refresh data is end in no more to sub ")
                break

            href = items.xpath('.//a/@href')
            if len(href) > 0:
                hyper = href[0].extract()
                hyperUrl = 'https://www.chacha.top' + hyper + '&justindex=' + str(self.startUrlIndex[response.url]) # 为了使hyuperUrl不一样

                self.hyperIndexMap[hyperUrl] = index
                self.fromUrl[hyperUrl] = response.url

                logging.info('current index ---------->  ' + str(index) + ' ---- '  + str(startLen))

                if self.isHyperAnn(hyperUrl):
                    yield Request(url=hyperUrl,callback=self.parseHyperAnn, dont_filter=True)
                elif self.isHyperPolicy(hyperUrl):
                    yield Request(url=hyperUrl,callback=self.parseHyperPolicy, dont_filter=True)
                else:
                    yield Request(url=hyperUrl,callback=self.parseHyperItem, dont_filter=True)



        if self.len[response.url] > startLen and noEnd: # 继续迭代爬取数据
            logging.info('parse move on  ----> ' + response.url)
            yield Request(url=response.url,callback=self.parse, dont_filter=True)
        else:
            logging.info('parse end ----> ' + str(startLen) + '--' + str(self.len[response.url]) + '---' + response.url)


    def isHyperlink(self, url):
        return self.isHyperAnn(url) or self.isHyperItem(url) or self.isHyperPolicy(url)

    def isHyperItem(self, url):
        return str(url).find('sup_item') != -1 or str(url).find('baidu') != -1

    def isHyperAnn(self, url):
        return str(url).find('announce') != -1 or str(url).find('publicity') != -1

    def isHyperPolicy(self, url):
        return str(url).find('sup_policy') != -1 or str(url).find('macro_policy') != -1 or str(url).find('imple_regu') != -1

    # 搜索 通知公示项
    # 通知申报 announce
    # 公示 publicity
    def parseHyperAnn(self, response):  # https://www.chacha.top/announce?id=274b53d9e06f3cc04c95
        logging.info('parse hyper announce publicity : ---> ' +  response.url)

        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = self.getType(response.url)
            com['url'] = response.url
            com['index'] = self.hyperIndexMap[response.url]
            com['fromUrl'] = self.fromUrl[response.url]

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
            leftBox = response.xpath('//div[@class="pull-left content-left policy-content-box bg-white m-b-md"]')
            leftContent = leftBox.xpath('div')
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
                    content = left.xpath('.//div[@class="detail-content"]').extract()
                    com['policyTrail'] = self.decodeStr(content).rstrip().lstrip()
                elif value.find('数据来源') != -1:
                    text = left.xpath('.//div/text()')
                    if len(text) > 0:
                        dataSourceDiv = text[0].extract()
                        com['dataSource'] = self.decodeStr(dataSourceDiv).replace("数据来源", "").replace("：","").rstrip().lstrip()
                else:
                    pass

            yield com

    # 搜索 扶持
    def parseHyperItem(self, response): # https://www.chacha.top/sup_item?id=aad86a5a974c55c59aaf
        logging.info('parse hyper sup_item : ---> ' +  response.url)
        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = self.getType(response.url)
            com['url'] = response.url
            com['index'] = self.hyperIndexMap[response.url]
            com['fromUrl'] = self.fromUrl[response.url]

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
            leftBox = response.xpath('//div[@class="pull-left content-left policy-content-box bg-white m-b-md"]')
            leftContent = leftBox.xpath('div')
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
                    content = left.xpath('.//div[@class="detail-content"]').extract()
                    com['policyTrail'] = self.decodeStr(content).rstrip().lstrip()
                elif value.find('数据来源') != -1:
                    text = left.xpath('.//div/text()')
                    if len(text) > 0:
                        dataSourceDiv = text[0].extract()
                        com['dataSource'] = self.decodeStr(dataSourceDiv).replace("数据来源", "").replace("：","").rstrip().lstrip()
                else:
                    pass

            yield com


    # 搜索 文件   相关政府政策文件 需要登录获取文件
    # 指导性文件 macro_policy
    # 扶持政策 sup_policy
    # 实施细则 imple_regu
    def parseHyperPolicy(self, response): # https://www.chacha.top/sup_policy?id=d0c7431587332fef3a27
        logging.info('parse hyper macro_policy sup_policy imple_regu: ---> ' +  response.url)
        if response.url != self.start_urls[0]:
            com = self.initItem()
            com['type'] = self.getType(response.url)
            com['url'] = response.url
            com['index'] = self.hyperIndexMap[response.url]
            com['fromUrl'] = self.fromUrl[response.url]

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
            leftBox = response.xpath('//div[@class="pull-left content-left bg-white m-b-md"]') #特殊的class
            leftContent = leftBox.xpath('div')
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
                    content = left.xpath('.//div[@class="detail-content"]').extract()
                    com['policyTrail'] = self.decodeStr(content).rstrip().lstrip()
                elif value.find('数据来源') != -1:
                    text = left.xpath('.//div/text()')
                    if len(text) > 0:
                        dataSourceDiv = text[0].extract()
                        com['dataSource'] = self.decodeStr(dataSourceDiv).replace("数据来源", "").replace("：","").rstrip().lstrip()

                else:
                    pass

            yield com


    def getType(self, url):
        if url.find('sup_policy') != -1: #文件  扶持
            return 'sup_policy'
        elif url.find('macro_policy') != -1:# 文件  指导性文件
            return 'macro_policy'
        elif url.find('imple_regu') != -1: #文件  实施细则
            return 'imple_regu'

        elif url.find('announce') != -1: # 通知 通知
            return 'announce'
        elif url.find('publicity') != -1: # 通知 公示
            return 'publicity'

        elif url.find('sup_item') != -1:  # 扶持
            return 'sup_item'

    def initItem(self):
        com = ChaXunItem()
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
        com['policyTrail'] = ''
        com['dataSource'] = ''
        com['fromUrl'] = ''
        return com

    def decodeStr(self, value):
        return json.dumps(value).decode('unicode_escape')


    def spider_closed(self, spider):   #当爬虫退出的时候 关闭chrome

        # index = self.index + 1    # 根据index 判断urls的数组长度, 再决定是否后续的添加
        # if index < len(self.start_urls):
        #     sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # ide调试
        #     execute(["scrapy","crawl","chacha", "-a", "index=" + str(index)])


        logging.info('close-------------------------> ' + spider.name)







