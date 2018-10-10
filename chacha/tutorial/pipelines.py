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

class TutorialPipeline(object):

    def __init__(self):

        self.wb = Workbook()
        self.ws = self.wb.active
        self.name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        self.ws.append(['标题', '发文体系', '文号', '序号',
                        '公示类型', '进度', '类型', '适用地区',
                        '发文时间', '扶持金额', '有效期限', '适用行业',
                        '政策分类', '详情', '政策轨迹', '文章地址',
                        '数据来源'
                        ])  # 设置表头


    def parseT(self, value):
                return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):
        if spider.name =="chacha":
            test = [
                    item['title'],      item['system'],     item['number'],     item['index'],
                    item['notetype'],   item['progress'],   item['type'],       item['area'],
                    item['updateTime'], item['money'],      item['validTime'],  item['industry'],
                    item['policyType'], item['content'],    item['policyTrail'], item['url'],
                    item['dataSource']
            ]
            self.ws.append(test)

            query = str(urlparse.urlparse(spider.browser.current_url).query)
            queryParams = dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])

            self.wb.save(spider.location + self.name + '-' + queryParams['query_text'].decode('utf-8') + '.xlsx')

            return item

        elif spider.name == 'check':

            # 判断 标题 test 是否存在 检测更新 入库
            # if item['test'] != '':
            #     sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            #     execute(["scrapy","crawl","chacha"])

            print 'check  pip save ' + item['test']

            return item


