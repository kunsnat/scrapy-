# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from openpyxl import Workbook

class TutorialPipeline(object):

    def __init__(self):

        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['标题', '进度', '类型', '适用地区', '发文时间', '扶持金额', '有效期限', '适用行业', '政策分类', '申报详情', '附件列表'])  # 设置表头


    def parseT(self, value):
                return json.dumps(value).decode('unicode_escape')

    def process_item(self, item, spider):
        test = [item['title'], item['progress'], item['type'], item['area'], item['updateTime'], item['money'], item['validTime'],
                item['industry'], item['policyType'], '' ]
        self.ws.append(test)
        self.wb.save(spider.location + 'chacha.xlsx')

        return item



