# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from openpyxl import Workbook
import urlparse
from scrapy.cmdline import execute
import os
import sys
import time
import logging

class TutorialPipeline(object):


    def parseT(self, value):
                return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):

        logging.info(" current pro item ----------->   : " + str(spider.name))

        if spider.name =="chaxun":
            row = [
                    item['title'],      item['system'],     item['number'],     item['index'],
                    item['notetype'],   item['progress'],   item['type'],       item['area'],
                    item['updateTime'], item['money'],      item['validTime'],  item['industry'],
                    item['policyType'], item['content'],    item['policyTrail'], item['url'],
                    item['dataSource']
            ]

            key = item['fromUrl']
            value = spider.workBookMap[key]

            value['ws'].append(row)  # 需要每个url对应一个 查询结果excel
            value['wb'].save(spider.location + spider.saveName)

            return item

        elif spider.name == 'check':

            # 判断 标题 test 是否存在 检测更新 入库
            # if item['test'] != '':
            #     sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            #     execute(["scrapy","crawl","chacha"])

            print 'check  pip save ' + item['test']

            return item

        elif spider.name == 'citys':
            row = [
                item['title'],      item['name'],     item['text'],     item['level'],
                item['id']
            ]

            key = item['url']
            value = self.citysWorkBoox(spider, key)

            value['ws'].append(row)  # 需要每个url对应一个 查询结果excel
            value['wb'].save(spider.location + self.mapCode(key) +  '.xlsx')

            return item

    # 区域名称 + 类型(扶持, 公示, 通知)
    def chachaCodeName(self, spider, url): # 省份, 城市, 区县 , province, city, district

        query = str(urlparse.urlparse(url).query)
        queryParams = dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
        if queryParams.has_key('district_code'):
            code = queryParams['district_code']
            return spider.codeName[code]
        elif queryParams.has_key('province_code'):
            code = queryParams['province_code']
            return spider.codeName[code]
        else:
            return 'china'

    def mapCode(self, url): # 省份, 城市, 区县 , province, city, district

        query = str(urlparse.urlparse(url).query)
        queryParams = dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
        if queryParams.has_key('city_code'):
            return queryParams['city_code']
        elif queryParams.has_key('province_code'):
            return queryParams['province_code']
        else:
            return 'china'



    def citysWorkBoox(self, spider, key):
        if dict(spider.workBookMap).has_key(key):
            return spider.workBookMap[key]

        else:
            wb = Workbook()
            ws = wb.active
            ws.append([
                'title', 'name', 'text', 'level',
                'id',

            ])  # 设置表头

            value = {'wb':'', 'ws':''}
            value['wb'] = wb
            value['ws'] = ws

            spider.workBookMap[key] = value

            return value



